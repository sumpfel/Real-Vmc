import socket
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import time


class VMCForwarder:
    def __init__(self, receive_ip='0.0.0.0', receive_port=39541,
                 send_ip='127.0.0.1', send_port=39539,
                 exclude_bones=None, exclude_blendshapes=None):

        self.receive_ip = receive_ip
        self.receive_port = receive_port
        self.send_ip = send_ip
        self.send_port = send_port
        self.exclude_bones = exclude_bones if exclude_bones else []
        self.exclude_blendshapes = exclude_blendshapes if exclude_blendshapes else []

        self.client = udp_client.SimpleUDPClient(self.send_ip, self.send_port)

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.set_default_handler(self._forward_handler)

        class ReusableOSCUDPServer(osc_server.ThreadingOSCUDPServer):
            def server_bind(server_self):
                server_self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_self.socket.bind(server_self.server_address)

        self.server = ReusableOSCUDPServer((self.receive_ip, self.receive_port), self.dispatcher)

    def _forward_handler(self, address, *args):
        # Filter bone messages
        if address.startswith("/VMC/Ext/Bone/"):
            if args and args[0] in self.exclude_bones:
                print(f"Excluded bone {args[0]} - skipping forwarding.")
                return

        # Filter blend shape messages
        if address == "/VMC/Ext/Blend/Val":
            if args and args[0] in self.exclude_blendshapes:
                print(f"Excluded blend shape {args[0]} - skipping forwarding.")
                return

        print(f"Forwarding {address} with args {args}")
        self.client.send_message(address, args)

    def send_bone_position_rotation(self, bone_name, xyz, rxryrzrw):
        address = "/VMC/Ext/Bone/Pos"
        args = [bone_name]+xyz+rxryrzrw
        print(f"Sending bone: {address} {args}")
        self.client.send_message(address, args)

    def send_blendshape_value(self, blendshape_name, value):

        address = "/VMC/Ext/Blend/Val"
        args = [blendshape_name, value]
        print(f"Sending blend shape: {address} {args}")
        self.client.send_message(address, args)

    def start(self):
        print(
            f"Starting VMC Forwarder: Receiving on {self.receive_ip}:{self.receive_port}, forwarding to {self.send_ip}:{self.send_port}")
        self.server.serve_forever()

    def shutdown(self):
        print("Shutting down VMC Forwarder.")
        self.server.shutdown()
        self.server.server_close()


if __name__ == "__main__":
    # Example exclusions
    exclude_bones = ['LeftLowerArm', 'LeftUpperArm', 'LeftHand']
    exclude_blendshapes = ['Blink', 'Smile']

    forwarder = VMCForwarder(exclude_bones=exclude_bones, exclude_blendshapes=exclude_blendshapes)

    import threading


    # Run the forwarder in a thread so we can send test messages while it's running
    def run_forwarder():
        forwarder.start()


    thread = threading.Thread(target=run_forwarder, daemon=True)
    thread.start()

    # Give server time to start
    time.sleep(1)

    try:
        while True:
            # Test sending bone messages
            forwarder.send_bone_position_rotation(
                "LeftLowerArm",
                [0, 0, 0],
                [0, .5, 1, 0]
            )  # Should forward even though it's in the exclude list (since this is an explicit send)

            forwarder.send_bone_position_rotation(
                "LeftHand",
                [0, 0, 0],
                [0, 1, .5, 1]
            )  # Should forward even though it's excluded

            # Test sending blend shape messages
            forwarder.send_blendshape_value("Happy", 0.85)  # Should forward
            forwarder.send_blendshape_value("Smile", 1.0)  # Should forward even though excluded

            time.sleep(0.1)
    except KeyboardInterrupt:
        forwarder.shutdown()
        print("exiting..")
