import xml.etree.ElementTree as ET
from csvHelper import init_csv, save_point_csv, load_point_csv
from point import Point6D
import time


class MotionController:

    # Command type 3 = gripp only
    COMMAND_TYPE_GRIP = 3

    # Gripper modes
    GRIP_MODE_JAW = 1
    GRIP_MODE_VACUUM = 2

    # Jaw direction modes, entscheiden ob oeffnen=1 oder schliessen=0
    JAW_DIRECTION_OPEN = 0
    JAW_DIRECTION_CLOSE = 1

    # Default jaw gripper values von motion_eki.src fuer servo gripper, wird geskippt weil pneumatisch, aber src file erwartets.
    DEFAULT_JAW_TOLERANCE = 50      # 0.5mm (value * 100)
    DEFAULT_JAW_VELOCITY = 50       # 50% speed
    DEFAULT_JAW_FORCE = 30          # grip force
    DEFAULT_JAW_BASE_POSITION = 75
    DEFAULT_JAW_WORK_POSITION = 4875
    DEFAULT_JAW_TEACH_POSITION = 3000
    DEFAULT_JAW_SHIFT_POSITION = 500


    def __init__(self, transport):
        self.transport = transport
        self.cmd_counter = 1

    def get_current_Point6D(self, name: str) -> Point6D:

        try:
            xml_bytes: bytes = self.transport.receive(800)
            print("RAW XML BYTES:", xml_bytes)
            # parse xml string

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

    def touchup(self, name: str, csv_file: str):
        point : Point6D = self.get_current_Point6D(name)
        save_point_csv(csv_file, point)
        return point

    def receive_motion_loop(self):
        """
        Thread that continuously receives actual robot position
        and prints it to the console.
        """
        while self.transport.connected:
            try:
                data = self.transport.socket.recv(4096)
                if not data:
                    print("Connection lost")
                    break

                #print("\nCurrent robot position:")
                #print(data)

            except Exception as e:
                print("Receive error:", e)
                break

            time.sleep(0.1)

    def _build_move_xml(self, cmd_id: int, point: Point6D, cmd_type: int = 1, mode: int = 1,
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

    def _send_move(self, point: Point6D, cmd_type, mode, vel, base, tool, blending):
        xml_bytes = self._build_move_xml(
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

    def _send_move_sequence(self, points: list[Point6D], cmd_type: int, mode: int, vel: float,
                           base: int = 0, tool: int = 0, blending: float = 0.0) -> None:
        """Build and send a sequence of move commands in one transmission.

        Concatenates individual EthernetKRL XML messages for each point and
        sends the combined bytes in a single call to the transport.

        Ids are assigned incrementally starting from the current cmd_counter.
        After sending, cmd_counter is advanced by the number of points.
        """
        if not points:
            print("No points provided for sequence.")
            return

        messages: list[bytes] = []
        next_id = self.cmd_counter
        for p in points:
            xml_bytes = self._build_move_xml(
                cmd_id=next_id,
                point=p,
                cmd_type=cmd_type,
                mode=mode,
                vel=vel,
                base=base,
                tool=tool,
                blending=blending
            )
            messages.append(xml_bytes)
            next_id += 1

        payload = b"".join(messages)
        self.transport.send(payload)
        print(f"Sequence sent with {len(points)} moves. Total bytes: {len(payload)}")
        self.cmd_counter = next_id

    def build_move_sequence_payload(self, points: list[Point6D], cmd_type: int, mode: int, vel: float,
                                    base: int = 0, tool: int = 0, blending: float = 0.0) -> bytes:
        """Build concatenated EthernetKRL XML payload for a sequence without sending.

        Returns bytes suitable for transport.send, and advances no counters.
        Useful for dry-run/offline testing and inspection.
        """
        if not points:
            return b""

        messages: list[bytes] = []
        next_id = self.cmd_counter
        for p in points:
            xml_bytes = self._build_move_xml(
                cmd_id=next_id,
                point=p,
                cmd_type=cmd_type,
                mode=mode,
                vel=vel,
                base=base,
                tool=tool,
                blending=blending
            )
            messages.append(xml_bytes)
            next_id += 1

        return b"".join(messages)

    def ptp(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self._send_move(point, cmd_type=1, mode=2, vel=vel, base=base, tool=tool, blending=blending)

    def lin(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self._send_move(point, cmd_type=1, mode=3, vel=vel, base=base, tool=tool, blending=blending)

    def circ(self, point: Point6D, vel, base=0, tool=0, blending=0.0):
        self._send_move(point, cmd_type=1, mode=4, vel=vel, base=base, tool=tool, blending=blending)

    # ==================== GRIPPER METHODS ====================

    # baut den xml string auf fuer den gripper command
    def _build_grip_xml(
        self,
        grip_mode: int,
        jaw_tolerance: int = 0,
        jaw_velocity: int = 0,
        jaw_force: int = 0,
        jaw_base_position: int = 0,
        jaw_work_position: int = 0,
        jaw_teach_position: int = 0,
        jaw_shift_position: int = 0,
        jaw_direction_mode: int = 0,
        vacuum_suction: int = 0,
        vacuum_cylinder: float = 0.0
    ) -> bytes:
        """Build XML command for gripper"""

        # RobotCommand Element mit Id und Type=3 (Grip)
        root = ET.Element("RobotCommand", Id=str(self.cmd_counter), Type=str(self.COMMAND_TYPE_GRIP))

        # Grip Element mit Mode
        grip = ET.SubElement(root, "Grip", Mode=str(grip_mode))

        # Jaw Element mit allen Attributen
        jaw = ET.SubElement(grip, "Jaw")
        jaw.set("Tolerance", str(jaw_tolerance))
        jaw.set("Velocity", str(jaw_velocity))
        jaw.set("Force", str(jaw_force))
        jaw.set("BasePosition", str(jaw_base_position))
        jaw.set("WorkPosition", str(jaw_work_position))
        jaw.set("TeachPosition", str(jaw_teach_position))
        jaw.set("ShiftPosition", str(jaw_shift_position))
        jaw.set("DirectionMode", str(jaw_direction_mode))

        # Vacuum Element
        vacuum = ET.SubElement(grip, "Vacuum")
        vacuum.set("Suction", str(vacuum_suction))
        vacuum.set("Cylinder", str(vacuum_cylinder))

        # XML zusammenbauen wie in _build_move_xml
        xml_body = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        full_message = f'<?xml version="1.0" encoding="UTF-8"?>\n<EthernetKRL>\n{xml_body}\n</EthernetKRL>\n'
        return full_message.encode("utf-8")


    def jaw_open(
        self,
        velocity: int = None,
        force: int = None,
        tolerance: int = None,
        base_position: int = None,
        work_position: int = None,
        teach_position: int = None,
        shift_position: int = None
    ) -> None:
        """Open the jaw gripper."""
        xml = self._build_grip_xml(
            grip_mode=self.GRIP_MODE_JAW,
            jaw_tolerance=tolerance if tolerance is not None else self.DEFAULT_JAW_TOLERANCE,
            jaw_velocity=velocity if velocity is not None else self.DEFAULT_JAW_VELOCITY,
            jaw_force=force if force is not None else self.DEFAULT_JAW_FORCE,
            jaw_base_position=base_position if base_position is not None else self.DEFAULT_JAW_BASE_POSITION,
            jaw_work_position=work_position if work_position is not None else self.DEFAULT_JAW_WORK_POSITION,
            jaw_teach_position=teach_position if teach_position is not None else self.DEFAULT_JAW_TEACH_POSITION,
            jaw_shift_position=shift_position if shift_position is not None else self.DEFAULT_JAW_SHIFT_POSITION,
            jaw_direction_mode=self.JAW_DIRECTION_OPEN
        )

        self.transport.send(xml)
        print(f" Jaw gripper OPEN command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1

    def jaw_close(
        self,
        velocity: int = None,
        force: int = None,
        tolerance: int = None,
        base_position: int = None,
        work_position: int = None,
        teach_position: int = None,
        shift_position: int = None
    ) -> None:
        """Close the jaw gripper."""
        xml = self._build_grip_xml(
            grip_mode=self.GRIP_MODE_JAW,
            jaw_tolerance=tolerance if tolerance is not None else self.DEFAULT_JAW_TOLERANCE,
            jaw_velocity=velocity if velocity is not None else self.DEFAULT_JAW_VELOCITY,
            jaw_force=force if force is not None else self.DEFAULT_JAW_FORCE,
            jaw_base_position=base_position if base_position is not None else self.DEFAULT_JAW_BASE_POSITION,
            jaw_work_position=work_position if work_position is not None else self.DEFAULT_JAW_WORK_POSITION,
            jaw_teach_position=teach_position if teach_position is not None else self.DEFAULT_JAW_TEACH_POSITION,
            jaw_shift_position=shift_position if shift_position is not None else self.DEFAULT_JAW_SHIFT_POSITION,
            jaw_direction_mode=self.JAW_DIRECTION_CLOSE
        )

        self.transport.send(xml)
        print(f" Jaw gripper CLOSE command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1


    def vacuum_on(self, cylinder: float = 0.0) -> None:
        """
        Turn vacuum gripper ON.

        Args:
            cylinder: Cylinder position, default 0.0
        """
        xml = self._build_grip_xml(
            grip_mode=self.GRIP_MODE_VACUUM,
            vacuum_suction=1,
            vacuum_cylinder=cylinder
        )

        self.transport.send(xml)
        print(f" Vacuum ON command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1


    def vacuum_off(self, cylinder: float = 0.0) -> None:
        """
        Turn vacuum gripper OFF.

        Args:
            cylinder: Cylinder position, default 0.0
        """
        xml = self._build_grip_xml(
            grip_mode=self.GRIP_MODE_VACUUM,
            vacuum_suction=0,
            vacuum_cylinder=cylinder
        )

        self.transport.send(xml)
        print(f" Vacuum OFF command sent (ID: {self.cmd_counter})")
        self.cmd_counter += 1