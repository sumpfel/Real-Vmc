from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def print_message(address, *args):
    print(f"Received message on {address} with arguments {args}")

def main():
    port = 39539
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(print_message)

    server = BlockingOSCUDPServer(("0.0.0.0", port), dispatcher)
    print(f"Serving on port {port}...")
    server.serve_forever()

if __name__ == "__main__":
    main()

#Received message on /VMC/Ext/Bone/Pos with arguments ('LeftLowerArm', 0, 0, 0, 0, 0.5, 1, 0)
#Received message on /VMC/Ext/Bone/Pos with arguments ('UpperChest', 6.390109774656594e-09, 0.1112809032201767, -0.012233471497893333, 0.0, -0.0036369371227920055, 0.009779175743460655, 0.9999455809593201)