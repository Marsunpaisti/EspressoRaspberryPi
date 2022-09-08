import struct
import threading
import time
import board
import digitalio
import pwmio
import adafruit_max31855
import warnings
import socket
import argparse
import os
import simulinkpid

parser = argparse.ArgumentParser(description="PID Control for Gaggia Classic Pro",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store",
                    help="Send data to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store",
                    help="Send data to port", default=7788)
parser.add_argument("-d", "--disableprints", action="store_true",
                    help="Disable prints", default=False),
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
DISABLE_PRINTS = config["disableprints"]
SAMPLING_INTERVAL = 0.5

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


latestCommandTimestamp = time.time()
latestTimeoutTimestamp = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
lastControlTimestamp = time.time()
startedTime = time.time()
pidController = simulinkpid.DiscretePid(0.046, 0.0018, -0.0030, 3.168544, 1, 0)
i = 0
steam_setpoint = 150.0
brew_setpoint = 94.0


def setHeaterDutyCycle(dutyCycleFraction: float):
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


def listenForUdpCommands(sock: socket.socket):
    global latestCommandTimestamp
    print("Listening for UDP comamnds")
    sock.bind(("0.0.0.0", DATA_SEND_PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            dutycycle, = struct.unpack("f", data)
            latestCommandTimestamp = time.time()
            setHeaterDutyCycle(dutycycle)
            if (not DISABLE_PRINTS):
                print(f"CMD: {dutycycle}")
        except OSError as e:
            if (not DISABLE_PRINTS):
                print(f"Socket closed")


def togglePump(enabled: bool):
    pumpPin.value = enabled


consecutiveReadTempFails = 0
latestValidTemp = 20


def readTemperature():
    """
    Returns the MAX31855K temperature in celcius.
    """
    global latestValidTemp
    global consecutiveReadTempFails

    try:
        latestValidTemp = max31855.temperature
        consecutiveReadTempFails = 0
        return latestValidTemp
    except RuntimeError as e:
        consecutiveReadTempFails = consecutiveReadTempFails + 1
        print(
            f"Error during readTemperature {e}. Returning latest valid temperature: {latestValidTemp}")
        if (consecutiveReadTempFails > 10):
            setHeaterDutyCycle(0)
            raise RuntimeError(
                "Too many consecutive temperature read failures.", e)
        return latestValidTemp


def sendToUdp(temperature: float, steamingSwitchState: int, brewSwitchState: int, msgIndex: int, output: float):
    global latestCommandTimestamp
    global latestTimeoutTimestamp
    global sock
    bytes = struct.pack("<ifbbf", int(msgIndex), temperature, int(
        steamingSwitchState), int(brewSwitchState), float(output))
    if (sock != None and DATA_SEND_IP != None):
        sock.sendto(bytes, (DATA_SEND_IP, DATA_SEND_PORT))
        if (not DISABLE_PRINTS):
            print(f"Sent data over UDP. Len: {len(bytes)}: {bytes}")


def controlLoop():
    global latestCommandTimestamp
    global latestTimeoutTimestamp
    global lastControlTimestamp
    global sock
    global i

    # Always feeding brew switch state to pump
    brewSwitch = not brewSwitchPin.value
    togglePump(brewSwitch)

    timeSinceLastSample = time.time() - lastControlTimestamp
    if (timeSinceLastSample < SAMPLING_INTERVAL):
        return
    i += 1
    elapsedTime = time.time() - startedTime
    boilerTemperature = readTemperature()
    heaterDutyCycle = heaterPin.duty_cycle / 65535
    steamingSwitch = not steamSwitchPin.value

    if (not DISABLE_PRINTS):
        print(f"T: {elapsedTime:.1f} Temp: {boilerTemperature:.1f} HeaterDutyCycle: {heaterDutyCycle:.2f} Steaming: {steamingSwitch:.0f}")

    # Setpoint control
    setpoint = brew_setpoint
    if (steamingSwitch):
        setpoint = steam_setpoint
    else:
        setpoint = brew_setpoint

    # PID Control
    pidOutput = pidController.step(
        float(setpoint - boilerTemperature), float(timeSinceLastSample))

    # Brew switch feedforward compensator
    compensatorOutput = 0.0
    # Sanity check for cases where brew switch might be intentionally activated to reduce temperature
    if (brewSwitch and not steamingSwitch and boilerTemperature < (setpoint + 6)):
        compensatorOutput = 0.14

    output = pidOutput + compensatorOutput
    # Clamp output
    if (output > 1):
        output = 1
    if (output < 0):
        output = 0

    # setHeaterDutyCycle(output)
    lastControlTimestamp = time.time()

    # Safety limit
    if (boilerTemperature > 165):
        setHeaterDutyCycle(0)

    # Send measurements over UDP
    setHeaterDutyCycle(0)
    sendToUdp(boilerTemperature, steamingSwitch, brewSwitch, i, output)

    return


def main():
    global sock
    print(f"Starting EspressoPi")
    if (DATA_SEND_IP):
        print(f"UDP Data send address set to {(DATA_SEND_IP,DATA_SEND_PORT)}")
    threading.Thread(target=listenForUdpCommands, args=(sock,)).start()

    while True:
        try:
            controlLoop()
        except Exception as e:
            setHeaterDutyCycle(0)
            raise Exception

        try:
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("Exiting")
            setHeaterDutyCycle(0)
            sock.close()
            os._exit(0)


if __name__ == "__main__":
    main()
