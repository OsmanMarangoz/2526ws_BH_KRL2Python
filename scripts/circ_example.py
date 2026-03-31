from time import sleep
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from robot import Robot
from command import Command
from point import Point6D

if __name__ == "__main__":
    database_dir = project_root / "database"

    KUKA_IP = "10.181.116.51"
    KUKA_PORT_META = 54601
    KUKA_PORT_MOTION = 54602

    kuka = Robot(KUKA_IP, KUKA_PORT_META, KUKA_PORT_MOTION)
    command = Command(kuka)

    kuka.connect()

    if kuka.motion_transport.connected:
        kuka.start_receive_threads()
        command.start_safety_thread()

        # Default settings
        kuka.set_default_velocity(0.1)
        kuka.set_default_base(15)
        kuka.set_default_tool(15)

        start0 = Point6D("start0", 150.0, 50.0, 50.0, 118.0, 89.0, 121.0)
        start1 = Point6D("start1", 150.0, 50.0, -0.1, 118.0, 89.0, 121.0)
        aux1   = Point6D("aux1",   100.0,100.0, -0.1, 118.0, 89.0, 121.0)
        end1   = Point6D("end1",   150.0,150.0, -0.1, 118.0, 89.0, 121.0)

        aux2   = Point6D("aux2",   200.0,100.0, -0.1, 118.0, 89.0, 121.0)
        end2   = Point6D("end2",   150.0, 50.0, -0.1, 118.0, 89.0, 121.0)

        kuka.ptp(start0)
        kuka.lin(start1)


        kuka.circ(end=end1, aux=aux1, vel=0.1)
        kuka.circ(end=end2, aux=aux2, vel=0.1)

        kuka.lin(start0)

        kuka.disconnect()