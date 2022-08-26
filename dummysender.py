from ast import arg
import struct
import time
import socket
import argparse

parser = argparse.ArgumentParser(description="Sends dummy data over UDP to target ip and port", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store", help="Target ip address", required=True)
parser.add_argument("-p", "--port", action="store", help="Target port", default=7788)
args = parser.parse_args()
config = vars(args)
IP = config["ip"]
PORT = config["port"]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        startedTime = time.time()
        i = 0
        while True:
            i += 1
            elapsedTime = time.time() - startedTime
            boilerTemperature = 123.4
            heaterDutycycle = 0.333
            packedDataBytes = struct.pack("!fff", elapsedTime, boilerTemperature, heaterDutycycle)
            print(f"Sending {packedDataBytes} to {(IP,PORT)}")
            sock.sendto(packedDataBytes, (IP, PORT))

            time.sleep(2.0)

if __name__ == "__main__":
    main()