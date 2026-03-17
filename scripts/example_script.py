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
        p1 = load_point_csv(str(database_dir / "points.csv"), "startpose") #homepose
        p2 = load_point_csv(str(database_dir / "points.csv"), "xp1") #pre pose lin
        p3 = load_point_csv(str(database_dir / "points.csv"), "xp2") #linear motion to pick pose muss lin
        p4 = load_point_csv(str(database_dir / "points.csv"), "xp3") #pick pose

        kuka.ptp(p1)

        kuka.jaw_open()

        kuka.lin(p2)
        kuka.lin(p3)
        kuka.lin(p4)

        kuka.jaw_close()
        sleep(0.5)

        kuka.lin(p3)
        kuka.lin(p2)
        kuka.ptp(p1)

        kuka.set_default_tool(15)
        # -------------------------------------------------
        # 4) Move Sequence
        # mehrere Punkte in einer Übertragung
        # -------------------------------------------------
        sequence_points = load_all_points_csv(str(database_dir / "sequence_points.csv"))

        kuka.move_sequence(
            points=sequence_points,
            mode=2,                     # ptp
            vel=0.15
        )

        while kuka.cmd_counter > kuka.last_finished_id + 1:
            print(kuka.last_finished_id, kuka.cmd_counter)
            sleep(0.5)

        kuka.disconnect()