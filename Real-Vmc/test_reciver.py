from pythonosc import dispatcher
from pythonosc import osc_server
import socket

def bone_handler(address, *args):
    print(f"Received {address} with args {args}")

class ReusableOSCUDPServer(osc_server.ThreadingOSCUDPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

if __name__ == "__main__":
    ip = "0.0.0.0"  # Listen on all interfaces
    port = 39541

    disp = dispatcher.Dispatcher()
    disp.map("/VMC/Ext/Bone/Pos", bone_handler)

    server = ReusableOSCUDPServer((ip, port), disp)
    print(f"Listening for OSC on {ip}:{port}")

    server.serve_forever()
