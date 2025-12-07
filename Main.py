import threading
import time

# communication | logic
from robot import Robot

# user interface
from command import Command


if __name__ == "__main__":

    KUKA_IP = "10.181.116.41"
    KUKA_PORT = 54602

    kuka = Robot(KUKA_IP, KUKA_PORT)
    kuka.connect()

    command = Command()
    
    if kuka.motion_transport.connected:
        # Thread for receiving actual position
        recv_thread = threading.Thread(
            target=kuka.receive_loop,
            daemon=True
        )
        recv_thread.start()

        # Thread for console input
        cmd_thread = threading.Thread(
            target=command.loop,
            daemon=True
        )
        cmd_thread.start()

        safety_thread = threading.Thread(
            target=command.safetyLoop,
            daemon=True
        )
        safety_thread.start()

        # Keep main thread alive
        while kuka.motion_transport.connected:
            time.sleep(0.5)