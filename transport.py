import socket

class TcpTransport:
    def __init__(self, ip: str, port: int, timeout: float = 3.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False

    def connect(self):
        if self.connected:
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.ip, self.port))
        self.connected = True
        print(f"Connected to {self.ip}:{self.port}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.connected = False

    def send(self, data: bytes):
        if not self.connected:
            raise RuntimeError("Not connected")
        self.socket.sendall(data)

    def receive(self, bufsize: int = 8192) -> bytes:
        if not self.connected:
            raise RuntimeError("Not connected")
        return self.socket.recv(bufsize)
