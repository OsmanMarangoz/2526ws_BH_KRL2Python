# threading
import threading
import time

# communication | logic
from robot import Robot

# user interface
from command import Command


if __name__ == "__main__":
    
    KUKA_IP = "10.181.116.71"
    KUKA_PORT_META = 54601
    KUKA_PORT_MOTION = 54602

    kuka = Robot(KUKA_IP, KUKA_PORT_META, KUKA_PORT_MOTION)
    kuka.connect()

    command = Command(kuka)
    
    if kuka.motion_transport.connected:

        # Thread for receiving actual position
        recv_motion_thread = threading.Thread(
            target=kuka.motion_visualization_loop,
            daemon=True
        )
        recv_motion_thread.start()

        recv_meta_thread = threading.Thread(
            target=kuka.receive_meta_loop,
            daemon=True
        )
        recv_meta_thread.start()

        # Thread for console input
        cmd_motion_thread = threading.Thread(
            target=command.loop,
            daemon=True
        )
        cmd_motion_thread.start()

        # Thread for safety
        cmd_safety_thread = threading.Thread(
            target=command.safetyLoop,
            daemon=True
        )
        cmd_safety_thread.start()

        # Keep main thread alive
        while kuka.motion_transport.connected:
            time.sleep(0.5)

