import struct
import time
import socket


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 7788))
        startedTime = time.time()
        i = 0
        while True:
            i += 1
            elapsedTime = time.time() - startedTime
            boilerTemperature = 123.4
            heaterDutycycle = 0.333
            packedDataBytes = struct.pack("!fff", elapsedTime, boilerTemperature, heaterDutycycle)
            print(f"Sending {packedDataBytes}")
            sock.sendto(packedDataBytes, ("255.255.255.255", 7788))

            time.sleep(2.0)

if __name__ == "__main__":
    main()
