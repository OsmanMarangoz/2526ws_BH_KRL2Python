import xml.etree.ElementTree as ET
from csvHelper import init_csv, save_point_csv, load_point_csv
from point import Point6D, JointState
import time
import pybullet as p
import pybullet_data
import math

class MotionController:
    def __init__(self, motionTransport):
        self.motionTransport = motionTransport
        self.cmd_counter = 0
        self.last_finished_id = 0

        self.default_velocity = 0.2
        self.default_acceleration = 0.2
        self.default_blending = 0.0
        self.default_base = 0
        self.default_tool = 15

        p.connect(p.GUI)
        p.setGravity(0,0,-9.81)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        urdf_path = r"/home/lukas/Dokumente/KRL2Python/kuka/kuka_kr3_support/urdf/kr3r540.urdf"
        self.robotURDF = p.loadURDF(urdf_path, useFixedBase=True)

    def _update_command_state(self):
        """Parse Command Id, Finished_Id and Stopped from lastMotionPacket."""
        try:
            xml_bytes: bytes = self.lastMotionPacket
            end_idx = xml_bytes.find(b"</RobotState>") + len(b"</RobotState>")
            xml_bytes = xml_bytes[:end_idx]

            root = ET.fromstring(xml_bytes.decode())

            cmd = root.find(".//Command")
            if cmd is not None:
                finished_id = cmd.get("Finished_Id")
                if finished_id is not None:
                    self.last_finished_id = int(finished_id)
        except Exception:
            pass  # don't crash on parse errors

    def _resolve_motion_params(self, vel=None, acc=None, base=None, tool=None, blending=None):
        vel = vel if vel is not None else self.default_velocity
        acc = acc if acc is not None else self.default_acceleration
        base = base if base is not None else self.default_base
        tool = tool if tool is not None else self.default_tool
        blending = blending if blending is not None else self.default_blending

        return vel, acc, base, tool, blending

    def set_default_velocity(self, vel: float):
        self.default_velocity = max(0.0, min(vel, 10.0))

    def set_default_acceleration(self, acc: float):
        self.default_acceleration = acc

    def set_default_blending(self, blending: float):
        self.default_blending = blending

    def set_default_base(self, base: int):
        self.default_base = base

    def set_default_tool(self, tool: int):
        self.default_tool = tool

    def get_current_Point6D(self, name: str) -> Point6D:

        try:
            xml_bytes: bytes = self.lastMotionPacket
            # print("RAW XML BYTES:", xml_bytes)

            end_idx = xml_bytes.find(b"</RobotState>") + len(b"</RobotState>")
            xml_bytes = xml_bytes[:end_idx]

            root = ET.fromstring(xml_bytes.decode())

            cart = root.find(".//Cartesian")
            if cart is None:
                raise ValueError("No Cartesian point found in received data!")

            point = Point6D(
                name=name,
                x=float(cart.get("X")),
                y=float(cart.get("Y")),
                z=float(cart.get("Z")),
                a=float(cart.get("A")),
                b=float(cart.get("B")),
                c=float(cart.get("C"))
            )
            return point

        except ET.ParseError:
            print(" ERROR: Failed to parse RobotState XML!")
            return None
        except Exception as e:
            print(f" ERROR while reading current point: {e}")
            return None

    def get_current_joint_state(self) -> JointState:
        try:
            xml_bytes: bytes = self.lastMotionPacket
            # print("RAW XML BYTES:", xml_bytes)

            end_idx = xml_bytes.find(b"</RobotState>") + len(b"</RobotState>")
            xml_bytes = xml_bytes[:end_idx]

            root = ET.fromstring(xml_bytes.decode())

            joint = root.find(".//Joint")
            if joint is None:
                raise RuntimeError("RobotState/Position/Joint not found")

            jointState = JointState(
                a1 = float(joint.get("A1")),
                a2 = float(joint.get("A2")),
                a3 = float(joint.get("A3")),
                a4 = float(joint.get("A4")),
                a5 = float(joint.get("A5")),
                a6 = float(joint.get("A6"))
            )
            return jointState
        
        except ET.ParseError:
            print(" ERROR: Failed to parse RobotState XML!")
            return None
        except Exception as e:
            print(f" ERROR while reading current point: {e}")
            return None

    def touchup(self, name: str, csv_file: str):
        point : Point6D = self.get_current_Point6D(name)
        save_point_csv(csv_file, point)
        return point

    def motion_visualization_loop(self):
        while self.motionTransport.connected:
            try:
                data = self.motionTransport.socket.recv(4096)
                if not data:
                    print("Motion connection lost")
                    break

                self.lastMotionPacket = data
                self._update_command_state()    

                joint_angles_deg = self.get_current_joint_state()
                if joint_angles_deg is None:
                    continue

                joint_angles = [
                math.radians(joint_angles_deg.a1),
                math.radians(joint_angles_deg.a2),
                math.radians(joint_angles_deg.a3),
                math.radians(joint_angles_deg.a4),
                math.radians(joint_angles_deg.a5),
                math.radians(joint_angles_deg.a6),
                ]
                #  joint_angles = [math.radians(a) for a in joint_angles_deg]

                for j in range(6):
                    p.resetJointState(self.robotURDF, j, joint_angles[j])

                p.stepSimulation()

            except self.motionTransport.socket.timeout:
                continue

            except Exception as e:
                print("Motion receive error:", e)
                break

            time.sleep(0.1)

    def _build_move_xml(self, cmd_id: int, point: Point6D, cmd_type: int, mode: int,
        vel: float, acc: float, base: int, tool: int, blending: float,
        wait_for_gripper: int = 0, aux_point: Point6D | None = None):
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

        if aux_point is not None:
            aux.set("X", str(aux_point.x))
            aux.set("Y", str(aux_point.y))
            aux.set("Z", str(aux_point.z))
            aux.set("A", str(aux_point.a))
            aux.set("B", str(aux_point.b))
            aux.set("C", str(aux_point.c))
        else:
            for k in ["X","Y","Z","A","B","C"]:
             aux.set(k, "0")

        joint = ET.SubElement(move, "Joint")
        for a in ["A1","A2","A3","A4","A5","A6"]:
            joint.set(a, "0")

        xml_body = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        full_message = f'<?xml version="1.0" encoding="UTF-8"?>\n<EthernetKRL>\n{xml_body}\n</EthernetKRL>\n'
        return full_message.encode("utf-8")

    def _send_move(self, point: Point6D, cmd_type, mode, vel, acc, base, tool, blending, aux_point: Point6D | None = None):
        xml_bytes = self._build_move_xml(
            cmd_id=self.cmd_counter,
            point=point,
            cmd_type=cmd_type,
            mode=mode,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending,
            aux_point=aux_point
        )

        self.motionTransport.send(xml_bytes)
        print(f"Move sent:\n{xml_bytes.decode()}")
        self.cmd_counter += 1

    def move_sequence(self, points: list[Point6D], mode: int, vel=None, acc=None, base=None, tool=None, blending=None) -> None:
        vel, acc, base, tool, blending = self._resolve_motion_params(vel=vel,acc=acc,base=base,tool=tool,blending=blending)

        if not points:
            print("No points provided for sequence.")
            return

        messages: list[bytes] = []
        next_id = self.cmd_counter
        for p in points:
            xml_bytes = self._build_move_xml(
                cmd_id=next_id,
                point=p,
                cmd_type=1,
                mode=mode,
                vel=vel,
                acc=acc,
                base=base,
                tool=tool,
                blending=blending
            )
            messages.append(xml_bytes)
            next_id += 1

        payload = b"".join(messages)
        self.motionTransport.send(payload)
        print(f"Sequence sent with {len(points)} moves. Total bytes: {len(payload)}")
        self.cmd_counter = next_id

    def ptp(self, point: Point6D, vel=None, acc=None, base=None, tool=None, blending=None):
        vel, acc, base, tool, blending = self._resolve_motion_params(vel=vel,acc=acc,base=base,tool=tool,blending=blending)

        self._send_move(
            point=point,
            cmd_type=1,
            mode=2,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def lin(self, point: Point6D, vel=None, acc=None, base=None, tool=None, blending=None):
        vel, acc, base, tool, blending = self._resolve_motion_params(vel=vel,acc=acc,base=base,tool=tool,blending=blending)

        self._send_move(
            point=point,
            cmd_type=1,
            mode=3,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def circ(self, end: Point6D, aux: Point6D, vel=None, acc=None, base=None, tool=None, blending=None):
        vel, acc, base, tool, blending = self._resolve_motion_params(vel=vel,acc=acc,base=base,tool=tool,blending=blending)

        self._send_move(
            point=end,
            cmd_type=1,
            mode=6,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending,
            aux_point=aux
        )

    # ==================== GRIPPER METHODS ====================

    # baut den xml string auf fuer den gripper command
    def _build_grip_xml(
        self,
        jaw_direction_mode: int = 0,

    ) -> bytes:
        """Build XML command for gripper"""

        # RobotCommand Element mit Id und Type=3 (Grip only)
        root = ET.Element("RobotCommand", Id=str(self.cmd_counter), Type="3")
        grip = ET.SubElement(root, "Grip")
        jaw = ET.SubElement(grip, "Jaw")
        jaw.set("DirectionMode", str(jaw_direction_mode))

        xml_body = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        full_message = f'<?xml version="1.0" encoding="UTF-8"?>\n<EthernetKRL>\n{xml_body}\n</EthernetKRL>\n'
        return full_message.encode("utf-8")

    def jaw_open(
        self,
    ) -> None:
        """Open the jaw gripper."""
        xml = self._build_grip_xml(
            jaw_direction_mode=0
        )

        self.motionTransport.send(xml)
        print(f"debug:\n{xml.decode()}")
        print(f" Jaw gripper OPEN command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1

    def jaw_close(
        self,
    ) -> None:
        """Close the jaw gripper."""
        xml = self._build_grip_xml(
            jaw_direction_mode=1
        )

        self.motionTransport.send(xml)
        print(f"debug:\n{xml.decode()}")
        print(f" Jaw gripper CLOSE command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1