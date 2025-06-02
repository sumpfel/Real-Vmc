from pythonosc import udp_client
import time

ip = "127.0.0.1"  # Receiver IP
port = 39541      # Receiver Port

client = udp_client.SimpleUDPClient(ip, port)

bone_name = "LeftLowerArm"
position = [0.1, 0.2, 0.3]         # x, y, z position
rotation = [0.0, 0.5, 1.0, 0.0]   # quaternion x, y, z, w

while True:
    args = [bone_name] + position + rotation
    client.send_message("/VMC/Ext/Bone/Pos", args)
    print(f"Sent /VMC/Ext/Bone/Pos {args}")
    time.sleep(0.5)
