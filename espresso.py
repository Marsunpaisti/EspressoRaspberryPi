import struct
import time
import board
import digitalio
import pwmio
import adafruit_max31855
import numpy as np
import warnings
import socket

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D8)
max31855 = adafruit_max31855.MAX31855(spi, cs)
heaterPin = pwmio.PWMOut(board.D4, frequency=1, duty_cycle=0, variable_frequency=False)
#heaterPin = digitalio.DigitalInOut(board.D4)
#heaterPin.switch_to_output(False)

def setHeaterDutyCycle(dutyCycleFraction: float):
    """
    Sets heater pin PWM duty cycle from dutyCycleFraction between (0-1), mapping it to (0 - 65535) accordingly
    """
    if (dutyCycleFraction > 1):
        warnings.warn(f"setHeaterDutyCycle dutyCycleFraction should be between 0 and 1, value was {dutyCycleFraction}. Clamped to 1.")
        dutyCycleFraction = 1
    if (dutyCycleFraction < 0):
        warnings.warn(f"setHeaterDutyCycle dutyCycleFraction should be between 0 and 1, value was {dutyCycleFraction}. Clamped to 0.")
        dutyCycleFraction = 0
    heaterPin.duty_cycle = round(dutyCycleFraction * 65535)

def readTemperature():
    """
    Returns the MAX31855K temperature in celcius.
    """
    return max31855.temperature



def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        startedTime = time.time()
        i = 0
        while True:
            i += 1

            elapsedTime = time.time() - startedTime
            boilerTemperature = readTemperature()
            heaterDutycycle = heaterPin.duty_cycle / 65535
            packedDataBytes = struct.pack("!fff", elapsedTime, boilerTemperature, heaterDutycycle)
            sock.sendto(packedDataBytes, ("255.255.255.255", 7788))

            print(f"Temperature: {boilerTemperature:.2f}")
            time.sleep(2.0)

if __name__ == "__main__":
    main()