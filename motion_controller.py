from motion_serializer import MotionSerializer
import xml.etree.ElementTree as ET
from csvHelper import init_csv, save_point_csv, load_point_csv
from point import Point6D
import time


class MotionController:
    def __init__(self, transport):
        self.transport = transport
        self.serializer = MotionSerializer()
        self.cmd_counter = 1

    def get_current_Point6D(self, name: str) -> Point6D:

        try:
            xml_bytes: bytes = self.transport.receive(4096)

            # parse xml string
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

    def receive_loop(self):
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
