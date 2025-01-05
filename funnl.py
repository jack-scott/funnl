# Goals
# - One file - mmmm maybe as few as possible, gotta hide the trash somewhere
# - Terminal UI / nice colours
# - Fun key pairing by some word mashing as docker does with container names
# - No server for now
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

from libs.word_mapper import PGPWordList
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription


import socketio

signal_server = "http://localhost:9999"

def connect_to_server():





if __name__ == "__main__":
    wl = PGPWordList()
    words = wl.choose_words(3)
    print(f"{words}")
    words = words + "-da"
    compl = wl.get_completions(words, num_words=3)
    print(f"{compl}")