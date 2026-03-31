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
from csvHelper import load_all_points_csv, load_point_csv

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
        kuka.set_default_base(0)
        kuka.set_default_tool(14)
        sleep(0.5)
        # -------------------------------------------------
        # 1) PTP zu gespeichertem Punkt
        # -------------------------------------------------
        p1 = load_point_csv(str(database_dir / "points.csv"), "xp1") #pre pose lin
        p2 = load_point_csv(str(database_dir / "points.csv"), "xp2") #linear motion to pick pose muss lin
        p3 = load_point_csv(str(database_dir / "points.csv"), "xp3") #pick pose
        p4 = load_point_csv(str(database_dir / "Haus_von_nikolaus_punkte.csv"), "H5")
        p5 = load_point_csv(str(database_dir / "points.csv"), "H0")
        p6 = load_point_csv(str(database_dir / "points.csv"), "H5_1")

        kuka.lin(p1)
        kuka.jaw_open()
        kuka.lin(p2)
        kuka.lin(p3)

        kuka.jaw_close()

        kuka.lin(p3)
        kuka.lin(p2)
        kuka.lin(p1)

        kuka.set_default_tool(15)
        kuka.ptp(p5)

        sequence_points = load_all_points_csv(str(database_dir / "Haus_von_nikolaus_punkte.csv"))

        kuka.move_sequence(
            points=sequence_points,
            mode=3,
            vel=0.10
        )
        kuka.lin(p6)

        kuka.set_default_tool(14)

        kuka.lin(p1)
        kuka.lin(p2)
        kuka.lin(p3)
        kuka.jaw_open()
        kuka.lin(p2)
        kuka.lin(p1)

        kuka.disconnect()