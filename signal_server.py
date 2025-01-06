# Borrowed from here, cheers
# https://github.com/pfertyk/webrtc-working-example

from aiohttp import web
import socketio
from libs.word_mapper import PGPWordList
import pickle

ROOM = "room"

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

offer_map = {}
sid_map = {}

wl = PGPWordList()


@sio.event
async def connect(sid, environ):
    print("Connected", sid)
    await sio.emit("ready", room=ROOM, skip_sid=sid)
    await sio.enter_room(sid, ROOM)


@sio.event
async def disconnect(sid):
    await sio.leave_room(sid, ROOM)
    print("Disconnected", sid)


@sio.event
async def request_connection(sid, data):
    requested_name = pickle.loads(data)
    print(f"Connection requested by {sid}")
    print(f"Requested name: {requested_name}")
    print(f"Offer map: {offer_map}")
    print(f"SID map: {sid_map}")

    if requested_name in sid_map:
        target_sid = sid_map[requested_name]
        print(f"Found target SID: {target_sid}")
        offer = offer_map[target_sid]
        print(f"Offer: {offer}")
        await sio.emit("target_connection", pickle.dumps(offer), room=ROOM)
    else:
        print("Offer not found")
        await sio.emit("no_target", room=sid)

@sio.event
async def offer_connection(sid, data):
    offer = pickle.loads(data)
    print(f"Connection offered by {sid}: {offer}")
    offer_map[sid] = offer
    nice_name = wl.choose_words(3)
    sid_map[nice_name] = sid
    print(f"Offer map: {offer_map}")
    print(f"SID map: {sid_map}")
    await sio.emit("collect_name", nice_name, room=ROOM)


if __name__ == "__main__":
    web.run_app(app, port=9999)
