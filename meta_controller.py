import xml.etree.ElementTree as ET
import time

class MetaController:
    def __init__(self, metaTransport):
        self.metaTransport = metaTransport

    def receive_meta_loop(self):
        while self.metaTransport.connected:
            try:
                data = self.metaTransport.socket.recv(4096)
                # print(data)
                if not data:
                    print("Meta connection lost")
                    break

            except self.metaTransport.socket.timeout:
                continue

            except Exception as e:
                print("Meta receive error:", e)
                break

    def set_override(self, value: float):
        value = max(0.0, min(1.0, value))
        xml = self._build_xml(value, abort=0)
        print(f"Override sent:\n{xml.decode()}")
        self.metaTransport.send(xml)
        print(f" OVERRIDE: {value*100:.0f}%")

    def emergency_stop(self):
        xml = self._build_xml(0.0, abort=1)
        self.metaTransport.send(xml)
        print(f"Emergency stop sent:\n{xml.decode()}")

    def reset_abort(self):
        xml = self._build_xml(1.0, abort=0)
        self.metaTransport.send(xml)
        print(f"Reset sent:\n{xml.decode()}")

    def _build_xml(self, override, abort):
        root = ET.Element("MetaCommand",
            VelocityOverride=str(override),
            AbortCommands=str(abort)
        )
        xml_body = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        full_message = f'<?xml version="1.0" eencoding="UTF-8"?>\n<EthernetKRL>\n{xml_body}\n</EthernetKRL>\n'
        return full_message.encode("utf-8")
