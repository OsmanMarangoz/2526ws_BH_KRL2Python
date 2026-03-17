from time import sleep

from src.robot import Robot
from src.command import Command
from src.point import Point6D
from src.csvHelper import load_all_points_csv, load_point_csv

if __name__ == "__main__":

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
        kuka.set_default_tool(0)
        sleep(0.5)

        csv_path =  r"../database/points.csv"

        # -------------------------------------------------
        # 1) PTP zu gespeichertem Punkt
        # -------------------------------------------------
        p1 = load_point_csv(str(csv_path), "home") #homepose
        p2 = load_point_csv(str(csv_path), "xp1") #pre pose lin
        p3 = load_point_csv(str(csv_path), "xp2") #linear motion to pick pose muss lin
        p4 = load_point_csv(str(csv_path), "xp3") #pick pose

        kuka.ptp(p1)

        kuka.set_default_tool(14)

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
        sequence_points = load_all_points_csv(r"../database/sequence_points.csv")

        kuka.move_sequence(
            points=sequence_points,
            mode=2,                     # ptp
            vel=0.15
        )

        while kuka.cmd_counter > kuka.last_finished_id + 1:
            print(kuka.last_finished_id, kuka.cmd_counter)
            sleep(0.5)

        kuka.disconnect()