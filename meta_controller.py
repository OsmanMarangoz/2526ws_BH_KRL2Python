import xml.etree.ElementTree as ET
from point import Point6D
import time

class MetaController:
    def __init__(self, transport):
        self.transport = transport

    def receive_meta_loop(self):
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


    def set_override(self, value: float):
        value = max(0.0, min(1.0, value))
        xml = self._build_xml(value, abort=0)
        self.transport.send(xml)
        print(f" OVERRIDE: {value*100:.0f}%")

    def emergency_stop(self):
        xml = self._build_xml(0.0, abort=1)
        self.transport.send(xml)

    def reset_abort(self):
        xml = self._build_xml(1.0, abort=0)
        self.transport.send(xml)

    def _build_xml(self, override, abort):
        root = ET.Element("MetaCommand",
            VelocityOverride=str(override),
            AbortCommands=str(abort)
        )
        body = ET.tostring(root, encoding="utf-8").decode()
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<EthernetKRL>
{body}
</EthernetKRL>
'''.encode()
