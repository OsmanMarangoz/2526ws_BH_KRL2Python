from time import sleep

from robot import Robot
from command import Command
from point import Point6D
from csvHelper import load_all_points_csv, load_point_csv

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
        kuka.set_default_tool(15)
        
        # -------------------------------------------------
        # 1) PTP zu gespeichertem Punkt
        # -------------------------------------------------
        p1 = load_point_csv("points.csv", "H5")
        kuka.ptp(p1)

        # -------------------------------------------------
        # 2) LIN zu manuell erzeugtem Punkt
        # -------------------------------------------------
        p2 = Point6D("p2", 100, 200, 300, 0, 90, 0)
        kuka.lin(p2, vel=0.5)

        # -------------------------------------------------
        # 3) CIRC
        # aux = Zwischenpunkt auf dem Kreisbogen
        # end = Endpunkt der Kreisbewegung
        # -------------------------------------------------
        aux_point = Point6D("aux", 150, 250, 320, 0, 90, 0)
        end_point = Point6D("end", 200, 300, 300, 0, 90, 0)

        kuka.circ(end=end_point, aux=aux_point, vel=0.2)
        
        # -------------------------------------------------
        # 4) Move Sequence
        # mehrere Punkte in einer Übertragung
        # -------------------------------------------------
        sequence_points = load_all_points_csv("sequence_points.csv")

        kuka.move_sequence(
            points=sequence_points,
            mode=2,                     # ptp
            vel=0.15
        )

        while kuka.cmd_counter > kuka.last_finished_id + 1:
            print(kuka.last_finished_id, kuka.cmd_counter)
            sleep(0.5)

        kuka.disconnect()