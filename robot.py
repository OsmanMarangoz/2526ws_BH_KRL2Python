from motion_controller import MotionController
from meta_controller import MetaController
from transport import TcpTransport


class Robot(MotionController, MetaController):

    def __init__(self, ip = "10.181.116.41", port_meta: int = 54601, port_motion: int = 54602):
        self.motion_transport = TcpTransport(ip, port_motion)
        self.meta_transport   = TcpTransport(ip, port_meta)

        # MotionController initialisieren
        MotionController.__init__(self, transport=self.motion_transport)
        
        # MetaController initialisieren
        MetaController.__init__(self, transport=self.meta_transport)

    def connect(self):
        self.motion_transport.connect()
        self.meta_transport.connect()

    def disconnect(self):
        self.motion_transport.disconnect()
        self.meta_transport.disconnect()
        