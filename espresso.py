import struct
import time
import board
import digitalio
import pwmio
import adafruit_max31855
import warnings
import socket
import argparse

parser = argparse.ArgumentParser(description="Sends dummy data over UDP to target ip and port", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store", help="Send data to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store", help="Send data to port", default=7788)
parser.add_argument("-r", "--interval", action="store", help="Sleep interval between reads", default=1),
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
SLEEP_INTERVAL = float(config["interval"])

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D8)
max31855 = adafruit_max31855.MAX31855(spi, cs)
heaterPin = pwmio.PWMOut(board.D4, frequency=1, duty_cycle=0, variable_frequency=False)

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
        startedTime = time.time()
        i = 0
        while True:
            i += 1
            elapsedTime = time.time() - startedTime
            boilerTemperature = readTemperature()
            heaterDutyCycle = heaterPin.duty_cycle / 65535
            packedDataBytes = struct.pack("!fff", elapsedTime, boilerTemperature, heaterDutyCycle)
            if (DATA_SEND_IP != None):
                print(f"Sending T: {elapsedTime} Temp: {boilerTemperature} HeaterDutyCycle: {heaterDutyCycle} to {(DATA_SEND_IP,DATA_SEND_PORT)}")
                sock.sendto(packedDataBytes, (DATA_SEND_IP, DATA_SEND_PORT))
            else:
                print(f"T: {elapsedTime} Temp: {boilerTemperature} HeaterDutyCycle: {heaterDutyCycle}")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
