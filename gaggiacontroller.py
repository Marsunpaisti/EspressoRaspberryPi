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
import asyncio

SAMPLING_INTERVAL = 0.5
P_GAIN = 0.046
I_GAIN = 0.0018
D_GAIN = -0.0030
FILTER_COEFF_N = 3.168544
OUTPUT_UPPER_LIMIT = 1.0
OUTPUT_LOWER_LIMIT = 0.0
DEFAULT_STEAM_SETPOINT = 150.0
DEFAULT_BREW_SETPOINT = 94.0

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D8)
max31855 = adafruit_max31855.MAX31855(spi, cs)
steamSwitchPin = digitalio.DigitalInOut(board.D23)
steamSwitchPin.switch_to_input(pull=digitalio.Pull.UP)
brewSwitchPin = digitalio.DigitalInOut(board.D12)
brewSwitchPin.switch_to_input(pull=digitalio.Pull.UP)
pumpPin = digitalio.DigitalInOut(board.D26)
pumpPin.switch_to_output(False)
heaterPin = pwmio.PWMOut(board.D4, frequency=2,
                         duty_cycle=0, variable_frequency=False)


class GaggiaController():
    def __init__(self, telemetryAddress, sio):
        self.sock = None
        if (telemetryAddress != None):
            self.telemetryAddress = telemetryAddress
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sampleNumber = 0
        self.sio = sio

        self.consecutiveReadTempFails = 0
        self.latestValidTemp = None
        self.__steam_setpoint = None
        self.__brew_setpoint = None
        self.__shot_time_limit = None
        with shelve.open("config", ) as cfg:
            try:
                self.__steam_setpoint = cfg["steam_setpoint"]
                self.__brew_setpoint = cfg["brew_setpoint"]
                self.__shot_time_limit = cfg["shot_time_limit"]
            except KeyError:
                pass
        if (self.__brew_setpoint == None):
            self.__brew_setpoint = DEFAULT_BREW_SETPOINT
        if (self.__steam_setpoint == None):
            self.__steam_setpoint = DEFAULT_STEAM_SETPOINT

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

    def stop(self):
        self.isRunning = False

    def __controlLoop(self):
        while self.isRunning:
            try:
                # Always feeding brew switch state to pump
                brewSwitch = not brewSwitchPin.value
                self.__setPumpEnabled(brewSwitch)

                self.__controlLoopLogic()
            except Exception as e:
                self.__setHeaterDutyCycle(0)
                raise e

            try:
                time.sleep(0.01)
            except KeyboardInterrupt:
                self.isRunning = False
                self.__setHeaterDutyCycle(0)
                self.__setPumpEnabled(False)
                heaterPin.deinit()

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
        setpoint = self.__brew_setpoint
        if (steamingSwitch):
            setpoint = self.__steam_setpoint

        if (setpoint == None):
            # Forcing type to be inferred as not None
            raise Exception("No setpoint??")

        # PID Control
        pidOutput = self.pidController.step(
            float(setpoint - boilerTemperature), float(SAMPLING_INTERVAL))

        # Brew switch feedforward compensator
        compensatorOutput = 0.0
        # Sanity check for cases where brew switch might be intentionally activated to reduce temperature
        if (brewSwitch and not steamingSwitch and boilerTemperature < (setpoint + 6.0)):
            compensatorOutput = 0.14

        output = pidOutput + compensatorOutput
        # Clamp output
        if (output > 1):
            output = 1
        if (output < 0):
            output = 0

        self.__setHeaterDutyCycle(output)

        # Safety limit
        if (boilerTemperature > 165):
            self.__setHeaterDutyCycle(0)

        # Send measurements over UDP
        self.__sendUdpTelemetry(
            boilerTemperature, steamingSwitch, brewSwitch, self.sampleNumber, output)

        res = self.__sendSocketIoTelemetry(boilerTemperature, output, setpoint)
        return

    async def __sendSocketIoTelemetry(self, temperature: float, dutyCycle: float, setpoint: float):
        if (self.sio == None):
            return
        telemetryData = {}
        telemetryData["temperature"] = temperature
        telemetryData["dutyCycle"] = dutyCycle
        telemetryData["setpoint"] = setpoint
        await self.sio.emit("telemetry", telemetryData)

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
        if (type(setpoint) == int or type(setpoint) == float and setpoint >= 70 and setpoint <= 99):
            self.__brew_setpoint = setpoint
            with shelve.open("config", ) as cfg:
                cfg["brew_setpoint"] = setpoint

            print(f"Brew setpoint set to {setpoint:.1f}")
            return True
        return False

    def setSteamSetpoint(self, setpoint: float):
        if (type(setpoint) == int or type(setpoint) == float and setpoint >= 110 and setpoint <= 160):
            self.__steam_setpoint = setpoint
            with shelve.open("config", ) as cfg:
                cfg["steam_setpoint"] = setpoint
            print(f"Steam setpoint set to {setpoint:.1f}")
            return True
        return False

    def setShotTimeLimit(self, limitSeconds: float):
        if (type(limitSeconds) == int or type(limitSeconds) == float and limitSeconds >= -1 and limitSeconds <= 50):
            self.__shot_time_limit = limitSeconds
            with shelve.open("config", ) as cfg:
                cfg["shot_time_limit"] = limitSeconds
            print(f"Shot time limit set to {limitSeconds:.1f}")
            return True
        return False

    def __del__(self):
        self.__setHeaterDutyCycle(0)
        self.__setPumpEnabled(False)
        self.isRunning = False
        if (self.sock != None):
            self.sock.close()
