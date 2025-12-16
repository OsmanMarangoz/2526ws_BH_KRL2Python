from motion_controller import MotionController
from meta_controller import MetaController
from transport import TcpTransport


class Robot(MotionController, MetaController):

    def __init__(self, ip:str, port_meta: int, port_motion: int):
        self.meta_transport   = TcpTransport(ip, port_meta)
        self.motion_transport = TcpTransport(ip, port_motion)

        # MotionController initialisieren
        MotionController.__init__(self, motionTransport=self.motion_transport)
        
        # MetaController initialisieren
        MetaController.__init__(self, metaTransport=self.meta_transport)

    def connect(self):
        self.motion_transport.connect()
        self.meta_transport.connect()

    def disconnect(self):
        self.motion_transport.disconnect()
        self.meta_transport.disconnect()
        