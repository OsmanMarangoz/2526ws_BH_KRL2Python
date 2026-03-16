import xml.etree.ElementTree as ET
import time
import socket

class MetaController:
    def __init__(self, metaTransport):
        self.metaTransport = metaTransport

    def receive_meta_loop(self):
        while self.metaTransport.connected:
            try:
                data = self.metaTransport.socket.recv(4096)
                print(data)
                if not data:
                    print("Meta connection lost")
                    break

            except self.metaTransport.socket.timeout:
                continue

            except Exception as e:
                print("Meta receive error:", e)
                break

    def set_override(self, value: int):  
        value = max(0, min(100, value))
        xml = self._build_xml(value, abort=0)
        print(f"Override sent:\n{xml.decode()}")
        self.metaTransport.send(xml)
        print(f" OVERRIDE: {value}%")

    def abort(self):
        xml = self._build_xml(0, abort=1)
        self.metaTransport.send(xml)
        print(f"Abort sent:\n{xml.decode()}")

    def _build_xml(self, override: int, abort: bool):
        full_message = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<EthernetKRL>\n'
            f'<MetaCommand VelocityOverride="{override}" AbortCommand="{abort}"></MetaCommand>\n'
            '</EthernetKRL>\n'
        )

        return full_message.encode("utf-8")