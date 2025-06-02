from pythonosc import udp_client
import time

ip = "127.0.0.1"  # Receiver IP
port = 39539      # Receiver Port

client = udp_client.SimpleUDPClient(ip, port)

bone_name = "LeftUpperArm"
position = [0.0, 0.0, 0.0]         # x, y, z position
rotation = [0.0, 0.0, 0.0, 10.0]   # quaternion x, y, z, w

blend_shape_name = "happy"
blend_shape_value = 1


args_bone2 = ["RightUpperArm"] + position + rotation
args_blend_shape = [blend_shape_name, blend_shape_value]

while True:
    position = [x+1 for x in position]
    rotation = [x+1 for x in rotation]
    args_bone = [bone_name] + position + rotation
    client.send_message("/VMC/Ext/Bone/Pos", args_bone)
    #client.send_message("/VMC/Ext/Blend/Val", args_blend_shape)
    #client.send_message("/VMC/Ext/Blend/Apply", [])
    print(f"Sent /VMC/Ext/Bone/Pos {args_bone}")
    #print(f"Sent /VMC/Ext/Blend/Val  {args_blend_shape}")
    time.sleep(0.5)