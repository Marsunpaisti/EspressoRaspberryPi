import threading
import socketio
import argparse
from gaggiacontroller import GaggiaController
from aiohttp import web


parser = argparse.ArgumentParser(description="PID Control and SocketIO server for Gaggia Classic Pro",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--ip", action="store",
                    help="Send UDP telemetry to ip address", required=False, default=None)
parser.add_argument("-p", "--port", action="store",
                    help="Send UDP telemetry to port", default=7788)
parser.add_argument("-d", "--disableprints", action="store_true",
                    help="Disable prints", default=False),
args = parser.parse_args()
config = vars(args)
DATA_SEND_IP = config["ip"]
DATA_SEND_PORT = config["port"]
DISABLE_PRINTS = config["disableprints"]

telemetryAddress = None
if (DATA_SEND_IP != None):
    telemetryAddress = (DATA_SEND_IP, DATA_SEND_PORT)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
gaggiaController = GaggiaController(telemetryAddress, sio, DISABLE_PRINTS)


async def index(request):
    """Serve the client-side application."""
    with open('./frontendBuild/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

app.router.add_static('/static', './frontendBuild/static')
app.router.add_get("/", index)


def debugPrint(text: str):
    if (DISABLE_PRINTS):
        return
    print(text)


@sio.event
def connect(sid, environ):
    debugPrint(f"New connection: {sid}")


@sio.on("set_brew_setpoint")
def set_brew_setpoint_handler(sid, data):
    return gaggiaController.setBrewSetpoint(data)


@sio.on("set_steam_setpoint")
def set_steam_setpoint_handler(sid, data):
    return gaggiaController.setSteamSetpoint(data)


@sio.on("set_shot_time_limit")
def set_shot_time_limit_handler(sid, data):
    return gaggiaController.setShotTimeLimit(data)


def startListening():
    web.run_app(app, port=8080)


if __name__ == "__main__":
    gaggiaController.start()
    listenerThread = threading.Thread(
        target=startListening, args=())
    listenerThread.start()
    listenerThread.join()
    gaggiaController.controlLoopThread.join()
