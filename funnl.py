# Goals
# - One file - mmmm maybe as few as possible, gotta hide the trash somewhere
# - Terminal UI / nice colours
# - Fun key pairing by some word mashing as docker does with container names
# - No server for now - actually found some example server code, I think its actually easier to prototype with a server
# - Easy to use


# General flow the the signaling server uses
# - Receives a hello connection from a new unique ID
#     - Send ACK with the human readable ID
#     - Future  - Assign a currently unused human readable ID
#               - Maintain this list of unique and human readable ID’s
# - Future - Receive keep alive ping from unique ID
#     - Future - Reset the lease on the human readable ID
# - Receive offer from unique ID for human-readable ID
#     - Forward offer to the receiver
#     - Future  - Make sure both sender and receiver are registered
#               - Keep track of offer count and make sure we are not getting rejected a lot
#               - Update lease on their ID’s
# - Receive accept from unique ID for human-readable ID
#     - Forward message to receiver
#     - Future  - make sure a request was initiated between these pairs
#               - decrement offer count so that we can see there are no more outstanding offers
#               - make sure sender and reciever are registered
# - Receive decline from unique ID for human readable ID
#     - Forward message to receiver
#     - Future  - make sure a request was initiated between these pairs
#               - increment refuse offer count so that we can see number of refusals
#               - make sure sender and reciever are registered
# - Should be fine to just send a JSON object over a websocket


# Can I get away with not using a signalling server?

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription


import socketio
import asyncio
import pickle
import argparse

class RTCSession:
    def __init__(self, signal_server="http://localhost:9999"):
        self.signal_server = signal_server
        self.sio = socketio.Client()
        self.pc = RTCPeerConnection()

        self.sio.on("connect", self.on_connect)
        self.sio.on("connect_error", self.on_connect_error)
        self.sio.on("disconnect", self.on_disconnect)

        self.pc.on("icecandidate", self.on_icecandidate)
        self.pc.on("iceconnectionstatechange", self.on_iceconnectionstatechange)

    def connect_to_server(self):
        self.sio.connect(self.signal_server)

    def on_connect(self):
        print("Connected to signaling server")

    def on_connect_error(self, data):
        print("Failed to connect to signaling server")

    def on_disconnect(self):
        print("Disconnected from signaling server")

    async def on_icecandidate(self, candidate):
        print(f"New ICE candidate: {candidate}")
        # Send the candidate to the remote peer via signaling server

    async def on_iceconnectionstatechange(self):
        print(f"ICE connection state is {self.pc.iceConnectionState}")
        if self.pc.iceConnectionState == "failed":
            await self.pc.close()

    def on_open(self):
        print("Data channel is open")

    def on_message(self, message):
        print(f"Received message: {message}")

class RTCReceiver(RTCSession):
    def __init__(self, signal_server="http://localhost:9999"):
        super().__init__(signal_server)
        self.connect_to_server()
        self.sio.on("target_connection", self.on_target_connection)
        self.sio.on("no_target", self.on_no_target)
        
        self.target_offer = None
        self.wait_for_input()

    async def open_connection(self):
        while self.target_offer is None:
            print("Waiting for target offer...")
            await asyncio.sleep(1)

        print(f"Received target offer: {self.target_offer}")

        # Assuming `offer` is the received offer from the remote peer
        await self.pc.setRemoteDescription(self.target_offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        print(f"Created answer: {answer.sdp}")


    def wait_for_input(self):
        print("Waiting for input")
        my_input = input("Press enter to continue:  ")
        print(f"Received input: {my_input}")
        # take input and request connection
        self.sio.emit("request_connection", pickle.dumps(my_input))


    def on_target_connection(self, data):
        target_offer = pickle.loads(data)
        print(f"Received target connection: {target_offer}")
        self.target_offer = target_offer
        # Assuming `offer` is the received offer from the remote peer
        asyncio.run(self.open_connection())


    def on_no_target(self):
        print("No target found, try again")
        self.wait_for_input()

class RTCSender(RTCSession):
    def __init__(self, signal_server="http://localhost:9999"):
        super().__init__(signal_server)
        self.connect_to_server()
        self.sio.on("collect_name", self.on_collect_name)
        self.my_name = None
        asyncio.run(self.create_rtc_connection())

    async def create_rtc_connection(self):
        # Add a data channel
        self.data_channel = self.pc.createDataChannel("chat")

        self.data_channel.on("open", self.on_open)
        self.data_channel.on("message", self.on_message)

        # Create an offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        print(f"Created offer: {offer.sdp}")

        offer_message = pickle.dumps(offer)
        print(f"Sending offer to signaling server")
        self.send_offer(offer_message)
        # Send the offer to the remote peer via signaling server
        # Wait for the answer from the remote peer
        # Assuming `answer` is the received answer from the remote peer
        # await self.pc.setRemoteDescription(answer)
        while self.my_name is None:
            print("Waiting for name...")
            await asyncio.sleep(1)
        print(f"My name is: {self.my_name}")

        return self.pc

    def send_offer(self, offer):
        self.sio.emit("offer_connection", offer)

    def on_collect_name(self, data):
        print(f"Received collect name: {data}")
        self.my_name = data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTC Session")
    parser.add_argument("--mode", choices=["dump", "receive"], required=True, help="Mode to run the RTC session")
    args = parser.parse_args()

    if args.mode == "dump":
        print("Running in dump mode")
        conn = RTCSender()
        # Spin and wait for the connection to be established
        asyncio.run(asyncio.sleep(3600))  # Run the event loop for 1 hour

    elif args.mode == "receive":
        print("Running in receive mode")
        conn = RTCReceiver()
        # Spin and wait for the connection to be established
        asyncio.run(asyncio.sleep(3600))  # Run the event loop for 1 hour



    # wl = PGPWordList()
    # words = wl.choose_words(3)
    # print(f"{words}")
    # words = words + "-da"
    # compl = wl.get_completions(words, num_words=3)
    # print(f"{compl}")