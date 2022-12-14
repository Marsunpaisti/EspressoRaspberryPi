import os
import struct
import threading
import time
import warnings
import board
import digitalio
import pwmio
import adafruit_max31855
import socket
import simulinkpid
import shelve
import atexit
import eventlet

eventlet.monkey_patch()

SAMPLING_INTERVAL = 0.5
P_GAIN = 0.046
I_GAIN = 0.0018
D_GAIN = -0.0030
FILTER_COEFF_N = 3.168544
OUTPUT_UPPER_LIMIT = 1.0
OUTPUT_LOWER_LIMIT = 0.0
DEFAULT_STEAM_SETPOINT = 150.0
DEFAULT_BREW_SETPOINT = 94.0
DEFAULT_BREW_FEEDFORWARD_COMPENSATION = 0.14

STEAM_PIN = board.D23
BREW_PIN = board.D12
PUMP_PIN = board.D26
SPI_CS_PIN = board.D8
HEATER_PIN = board.D4

spi = board.SPI()
cs = digitalio.DigitalInOut(SPI_CS_PIN)
max31855 = adafruit_max31855.MAX31855(spi, cs)
steamSwitchPin = digitalio.DigitalInOut(STEAM_PIN)
steamSwitchPin.switch_to_input(pull=digitalio.Pull.UP)
brewSwitchPin = digitalio.DigitalInOut(BREW_PIN)
brewSwitchPin.switch_to_input(pull=digitalio.Pull.UP)
pumpPin = digitalio.DigitalInOut(PUMP_PIN)
pumpPin.switch_to_output(False)
heaterPin = pwmio.PWMOut(HEATER_PIN, frequency=2,
                         duty_cycle=0, variable_frequency=False)
DISABLE_PRINTS = False


def debugPrint(text: str):
    if (DISABLE_PRINTS):
        return
    print(text)


class GaggiaController():
    def __init__(self, sio, telemetryAddress, onTelemetryCallback, disablePrints):
        atexit.register(self.__disableOutputsAndExit)
        global DISABLE_PRINTS
        self.disablePrints = disablePrints
        DISABLE_PRINTS = disablePrints
        self.sock = None
        self.sio = sio
        if (telemetryAddress != None):
            self.telemetryAddress = telemetryAddress
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sampleNumber = 0
        self.onTelemetryCallback = onTelemetryCallback

        self.consecutiveReadTempFails = 0
        self.latestValidTemp = None
        self.steam_setpoint = DEFAULT_STEAM_SETPOINT
        self.brew_setpoint = DEFAULT_BREW_SETPOINT
        self.brew_feedforward_compensation = DEFAULT_BREW_FEEDFORWARD_COMPENSATION
        self.shot_time_limit = 0
        self.__brewStarted = 0
        self.__brewStopped = 0
        self.__lastBrewSwitchState = False
        with shelve.open("config", ) as cfg:
            try:
                self.steam_setpoint = cfg["steam_setpoint"]
            except KeyError:
                pass
            try:
                self.brew_setpoint = cfg["brew_setpoint"]
            except KeyError:
                pass
            try:
                self.shot_time_limit = cfg["shot_time_limit"]
            except KeyError:
                pass
            try:
                self.brew_feedforward_compensation = cfg["brew_feedforward_compensation"]
            except KeyError:
                pass

        if (self.shot_time_limit == None):
            self.shot_time_limit = 0
        if (self.brew_setpoint == None):
            self.brew_setpoint = DEFAULT_BREW_SETPOINT
        if (self.steam_setpoint == None):
            self.steam_setpoint = DEFAULT_STEAM_SETPOINT

        self.pidController = simulinkpid.DiscretePid(
            P_GAIN, I_GAIN, D_GAIN, FILTER_COEFF_N, OUTPUT_UPPER_LIMIT, OUTPUT_LOWER_LIMIT)

    def start(self):
        self.lastSampleTimestamp = time.time()
        self.startedTime = time.time()
        self.isRunning = True
        self.__setHeaterDutyCycle(0)
        self.controlLoopThread = threading.Thread(
            target=self.__controlLoop, args=())
        self.controlLoopThread.start()
        debugPrint("Gaggia Controller Started")

    def stop(self):
        self.isRunning = False

    def __trackShotDuration(self):
        brewSwitchState = not brewSwitchPin.value
        if (brewSwitchState and not self.__lastBrewSwitchState):
            self.__brewStarted = time.time()
        if (not brewSwitchState and self.__lastBrewSwitchState and self.__brewStopped < self.__brewStarted):
            self.__brewStopped = time.time()
        self.__lastBrewSwitchState = brewSwitchState

    def __limitShotDuration(self):
        steamingSwitchState = not steamSwitchPin.value
        isShotTimerEnabled = self.shot_time_limit != None and self.shot_time_limit > 0
        if (isShotTimerEnabled and not steamingSwitchState):
            brewDurationSeconds = round(time.time() - self.__brewStarted, 1)
            if (brewDurationSeconds >= self.shot_time_limit):
                self.__setPumpEnabled(False)
                if (self.__brewStopped < self.__brewStarted):
                    self.__brewStopped = time.time()
                return True
        return False

    def __controlLoop(self):
        while self.isRunning:
            try:
                # Always feeding brew switch state to pump
                brewSwitch = not brewSwitchPin.value
                self.__trackShotDuration()
                if (not self.__limitShotDuration()):
                    self.__setPumpEnabled(brewSwitch)

                self.__controlLoopLogic()
            except Exception as e:
                print(e)
                self.__disableOutputsAndExit()

            try:
                self.sio.sleep(0.1)
            except KeyboardInterrupt:
                self.__disableOutputsAndExit()

    def __disableOutputsAndExit(self):
        self.isRunning = False
        self.__setHeaterDutyCycle(0)
        self.__setPumpEnabled(False)
        heaterPin.deinit()
        pumpPin.deinit()

        digitalio.DigitalInOut(HEATER_PIN).switch_to_input(
            pull=digitalio.Pull.DOWN)
        digitalio.DigitalInOut(BREW_PIN).switch_to_input(
            pull=digitalio.Pull.DOWN)
        digitalio.DigitalInOut(STEAM_PIN).switch_to_input(
            pull=digitalio.Pull.DOWN)
        digitalio.DigitalInOut(PUMP_PIN).switch_to_input(
            pull=digitalio.Pull.DOWN)
        digitalio.DigitalInOut(SPI_CS_PIN).switch_to_input(
            pull=digitalio.Pull.DOWN)
        os._exit(1)

    def __controlLoopLogic(self):
        timeSinceLastSample = time.time() - self.lastSampleTimestamp
        if (timeSinceLastSample < SAMPLING_INTERVAL):
            return

        self.lastSampleTimestamp = time.time()
        self.sampleNumber += 1
        boilerTemperature = self.__readTemperature()
        if (boilerTemperature == None):
            self.__setHeaterDutyCycle(0)
            return

        brewSwitch = not brewSwitchPin.value
        steamingSwitch = not steamSwitchPin.value

        # Setpoint control
        setpoint = self.brew_setpoint
        if (steamingSwitch):
            setpoint = self.steam_setpoint

        if (setpoint == None):
            # Forcing type to be inferred as not None
            raise Exception("No setpoint??")

        # PID Control
        pidOutput = self.pidController.step(
            float(setpoint - boilerTemperature), float(SAMPLING_INTERVAL))

        # Brew switch feedforward compensator
        compensatorOutput = 0.0
        # Sanity check for cases where brew switch might be intentionally activated to reduce temperature
        if (pumpPin.value == True and not steamingSwitch and boilerTemperature < (setpoint + 6.0)):
            compensatorOutput = DEFAULT_BREW_FEEDFORWARD_COMPENSATION

        output = pidOutput + compensatorOutput
        # Clamp output
        if (output > 1):
            output = 1
        if (output < 0):
            output = 0

        self.__setHeaterDutyCycle(output)

        # Safety limit
        if (boilerTemperature > 175):
            self.__setHeaterDutyCycle(0)

        # Send measurements over UDP
        self.__sendUdpTelemetry(
            boilerTemperature, steamingSwitch, brewSwitch, self.sampleNumber, output)

        self.__handleTelemetryCallback(
            boilerTemperature, setpoint)
        return

    def __handleTelemetryCallback(self, temperature: float, setpoint: float):
        shotDuration = self.__brewStopped - self.__brewStarted
        if (self.__brewStopped < self.__brewStarted):
            shotDuration = time.time() - self.__brewStarted
        telemetryData = {}
        telemetryData["ts"] = round(time.time()*1000)
        telemetryData["temp"] = round(temperature, 2)
        telemetryData["set"] = round(setpoint, 1)
        telemetryData["shotdur"] = round(shotDuration, 1)
        if (self.onTelemetryCallback == None):
            return
        self.onTelemetryCallback(telemetryData)

    def __sendUdpTelemetry(self, temperature: float, steamingSwitchState: int, brewSwitchState: int, msgIndex: int, output: float):
        if (self.sock == None):
            return
        bytes = struct.pack("<ifbbf", int(msgIndex), temperature, int(
            steamingSwitchState), int(brewSwitchState), float(output))
        self.sock.sendto(bytes, self.telemetryAddress)

    def __readTemperature(self):
        """
        Returns the MAX31855K temperature in celcius, or None if not available.
        """

        try:
            self.latestValidTemp = max31855.temperature
            self.consecutiveReadTempFails = 0
            return self.latestValidTemp
        except RuntimeError as e:
            self.consecutiveReadTempFails = self.consecutiveReadTempFails + 1
            print(
                f"Error during readTemperature {e}. Returning latest valid temperature: {self.latestValidTemp}")
            if (self.consecutiveReadTempFails > 10):
                self.__setHeaterDutyCycle(0)
                raise RuntimeError(
                    "Too many consecutive temperature read failures.", e)

    def __setPumpEnabled(self, state: bool):
        pumpPin.value = state

    def __setHeaterDutyCycle(self, dutyCycleFraction: float):
        """
        Sets heater pin PWM duty cycle from dutyCycleFraction between (0-1), mapping it to (0 - 65535) accordingly
        """
        if (dutyCycleFraction > 1.0):
            warnings.warn(
                f"setHeaterDutyCycle dutyCycleFraction should be between 0 and 1, value was {dutyCycleFraction}. Clamped to 1.")
            dutyCycleFraction = 1.0
        if (dutyCycleFraction < 0.0):
            warnings.warn(
                f"setHeaterDutyCycle dutyCycleFraction should be between 0 and 1, value was {dutyCycleFraction}. Clamped to 0.")
            dutyCycleFraction = 0.0
        heaterPin.duty_cycle = round(dutyCycleFraction * 65535)

    def setBrewSetpoint(self, setpoint: float):
        if (type(setpoint) == int or type(setpoint) == float and setpoint >= 80 and setpoint <= 110):
            self.brew_setpoint = setpoint
            with shelve.open("config", ) as cfg:
                cfg["brew_setpoint"] = setpoint

            debugPrint(f"Brew setpoint set to {setpoint:.1f}")
            return True
        return False

    def setSteamSetpoint(self, setpoint: float):
        if (type(setpoint) == int or type(setpoint) == float and setpoint >= 120 and setpoint <= 160):
            self.steam_setpoint = setpoint
            with shelve.open("config", ) as cfg:
                cfg["steam_setpoint"] = setpoint
            debugPrint(f"Steam setpoint set to {setpoint:.1f}")
            return True
        return False

    def setShotTimeLimit(self, limitSeconds: float):
        if (type(limitSeconds) == int or type(limitSeconds) == float and limitSeconds >= 0 and limitSeconds <= 45):
            self.shot_time_limit = limitSeconds
            with shelve.open("config", ) as cfg:
                cfg["shot_time_limit"] = limitSeconds
            debugPrint(f"Shot time limit set to {limitSeconds:.1f}")
            return True
        return False

    def setBrewFeedForwardCompensation(self, brewCompensation: float):
        if (type(brewCompensation) == int or type(brewCompensation) == float and brewCompensation >= 0 and brewCompensation <= 0.3):
            self.brew_feedforward_compensation = brewCompensation
            with shelve.open("config", ) as cfg:
                cfg["brew_feedforward_compensation"] = brewCompensation
            debugPrint(
                f"Brew feedforward compensation set to {brewCompensation:.2f}")
            return True
        return False

    def __del__(self):
        self.__setHeaterDutyCycle(0)
        self.__setPumpEnabled(False)
        self.isRunning = False
        if (self.sock != None):
            self.sock.close()
