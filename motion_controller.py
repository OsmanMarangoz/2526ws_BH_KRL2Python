from motion_serializer import MotionSerializer
from state_parser import point_from_state
from points_io import save_point_csv
from point import Point6D
import time


class MotionController:
    def __init__(self, transport):
        self.transport = transport
        self.serializer = MotionSerializer()
        self.cmd_counter = 1

    def get_current_pose(self, name="unnamed"):
        data = self.transport.receive(4096)
        return point_from_state(data, name)

    def touchup(self, name: str, csv_file: str):
        point = self.get_current_pose(name)
        save_point_csv(csv_file, point)
        print(f"Touchup stored: {point}")
        return point

    def send_move(self, point: Point6D, cmd_type, mode, vel, base, tool, blending):
        xml_bytes = self.serializer.to_xml(
            cmd_id=self.cmd_counter, 
            point=point,
            cmd_type=cmd_type, 
            mode=mode, 
            vel=vel,
            base=base, 
            tool=tool, 
            blending=blending
        )

        self.transport.send(xml_bytes)
        print(f"Move sent:\n{xml_bytes.decode()}")
        self.cmd_counter += 1

    def ptp(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self.send_move(point, cmd_type=1, mode=2, vel=vel, base=base, tool=tool, blending=blending)

    def lin(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self.send_move(point, cmd_type=1, mode=3, vel=vel, base=base, tool=tool, blending=blending)

    def circ(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self.send_move(point, cmd_type=1, mode=4, vel=vel, base=base, tool=tool, blending=blending)
