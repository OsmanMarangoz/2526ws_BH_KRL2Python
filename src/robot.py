import threading
from time import sleep
from motion_controller import MotionController
from meta_controller import MetaController
from transport import TcpTransport


class Robot(MotionController, MetaController):

    def __init__(self, ip: str, port_meta: int, port_motion: int):
        self.meta_transport = TcpTransport(ip, port_meta)
        self.motion_transport = TcpTransport(ip, port_motion)

        # MotionController initialisieren
        MotionController.__init__(self, motionTransport=self.motion_transport)
        # MetaController initialisieren
        MetaController.__init__(self, metaTransport=self.meta_transport)

        self._meta_thread = None
        self._motion_thread = None

    def connect(self):
        self.motion_transport.connect()
        self.meta_transport.connect()

    def start_receive_threads(self):
        """
        self._meta_thread = threading.Thread(
            target=self.receive_meta_loop,
            daemon=True
        )
        self._meta_thread.start()
        """

        self._motion_thread = threading.Thread(
            target=self.motion_visualization_loop,
            daemon=True
        )
        self._motion_thread.start()

    def disconnect(self):
        if self.motion_transport.connected:
            while True:
                with self.data_lock:
                    if self.cmd_counter <= self.last_finished_id + 1:
                        print("cmd_counter:", self.cmd_counter, "last_finished_id:", self.last_finished_id)
                        break
                sleep(0.5)

        self.motion_transport.disconnect()
        self.meta_transport.disconnect()