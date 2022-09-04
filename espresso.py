import struct
import time
import board
import digitalio
import pwmio
import adafruit_max31855
import warnings
import socket
import argparse
import threading
import os

parser = argparse.ArgumentParser(description="Sends dummy data over UDP to target ip and port", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store", help="Send data to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store", help="Send data to port", default=7788)
parser.add_argument("-r", "--interval", action="store", help="Sleep interval between reads", default=1),
parser.add_argument("-d", "--disableprints", action="store_true", help="Disable prints", default=False),
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
SLEEP_INTERVAL = float(config["interval"])
DISABLE_PRINTS = config["disableprints"]

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D8)
steamSwitchPin = digitalio.DigitalInOut(board.D23)
steamSwitchPin.switch_to_input(pull=digitalio.Pull.UP)
max31855 = adafruit_max31855.MAX31855(spi, cs)
heaterPin = pwmio.PWMOut(board.D4, frequency=1, duty_cycle=0, variable_frequency=False)
sock = None

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


def listenForUdpCommands(sock: socket.socket):
    print("Listening for UDP comamnds")
    sock.bind(("0.0.0.0", DATA_SEND_PORT))
    while True:
        try:    
            data, addr = sock.recvfrom(1024)        
            command, = struct.unpack("f", data)
            if (not DISABLE_PRINTS):
                print(f"Cmd: {command}")
        except OSError as e:
            if (not DISABLE_PRINTS):
                print(f"Socket closed")

def sendToUdp(temperature: float, steamingSwitchState: int):
    bytes = struct.pack("fb", temperature, steamingSwitchState)
    if (sock != None and DATA_SEND_IP != None):
        sock.sendto(bytes, (DATA_SEND_IP, DATA_SEND_PORT))
    
        if (not DISABLE_PRINTS):
            print(f"Sent data over UDP")

def main():
    print(f"Starting EspressoPi")
    if (DATA_SEND_IP):
        print(f"UDP Data send address set to {(DATA_SEND_IP,DATA_SEND_PORT)}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udpsock:
        sock = udpsock
        threading.Thread(target=listenForUdpCommands,args=(sock,)).start()
        
        startedTime = time.time()
        i = 0
        while True:
            i += 1
            elapsedTime = time.time() - startedTime
            boilerTemperature = readTemperature()
            heaterDutyCycle = heaterPin.duty_cycle / 65535
            steamingSwitch = not steamSwitchPin.value
            if (not DISABLE_PRINTS):
                print(f"T: {elapsedTime:.1f} Temp: {boilerTemperature:.1f} HeaterDutyCycle: {heaterDutyCycle:.2f} Steaming: {steamingSwitch:.0f}")
            sendToUdp(boilerTemperature, steamingSwitch)

            try: 
                time.sleep(SLEEP_INTERVAL)
            except KeyboardInterrupt:
                print("Exiting")
                sock.close()
                os._exit(0)

if __name__ == "__main__":
    main()
