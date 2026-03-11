from time import sleep

# communication | logic
from robot import Robot

# user interface
from command import Command

if __name__ == "__main__":
    
    KUKA_IP = "10.181.116.51"
    KUKA_PORT_META = 54601
    KUKA_PORT_MOTION = 54602

    kuka = Robot(KUKA_IP, KUKA_PORT_META, KUKA_PORT_MOTION)
    command = Command(kuka)
    
    kuka.connect()
    
    if kuka.motion_transport.connected:
        kuka.start_receive_threads()
        command.start_motion_thread()
        command.start_safety_thread()
       
        # Keep main thread alive
        while kuka.motion_transport.connected:
            sleep(0.5)