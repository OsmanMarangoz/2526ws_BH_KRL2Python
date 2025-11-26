import xml.etree.ElementTree as ET
from dataclasses import dataclass
from point import Point6D

class MotionSerializer:
    def to_xml(self, cmd_id: int, point: Point6D, cmd_type: int = 1, mode: int = 1, 
               vel: float = 0.5, acc: float = 0.5, base: int = 0, tool: int = 0, blending: float = 0.0,
               wait_for_gripper: int = 0):
        root = ET.Element("RobotCommand", Id=str(cmd_id), Type=str(cmd_type))
        move = ET.SubElement(root, "Move",
            Mode=str(mode),
            BaseIndex=str(base),
            ToolIndex=str(tool),
            Velocity=str(vel),
            Acceleration=str(acc),
            Blending=str(blending),
            WaitForGripper=str(wait_for_gripper)
        )
        cart = ET.SubElement(move, "Cartesian")
        cart.set("X", str(point.x))
        cart.set("Y", str(point.y))
        cart.set("Z", str(point.z))
        cart.set("A", str(point.a))
        cart.set("B", str(point.b))
        cart.set("C", str(point.c))

        aux = ET.SubElement(move, "Cartesian_Aux")
        for k in ["X","Y","Z","A","B","C"]:
            aux.set(k, "0")

        joint = ET.SubElement(move, "Joint")
        for a in ["A1","A2","A3","A4","A5","A6"]:
            joint.set(a, "0")

        xml_body = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        full_message = f'<?xml version="1.0" encoding="UTF-8"?>\n<EthernetKRL>\n{xml_body}\n</EthernetKRL>\n'
        return full_message.encode("utf-8")
    