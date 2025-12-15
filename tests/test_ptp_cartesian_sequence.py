import unittest
from pathlib import Path
import sys
#run with python3 -m unittest test_ptp_cartesian_sequence

# Ensure project modules are importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from csvHelper import load_all_points_csv
from motion_controller import MotionController


class DummyTransport:
    def __init__(self):
        self.connected = True
        self.sent_payloads: list[bytes] = []

    def send(self, data: bytes):
        # Capture all sent data for assertions
        self.sent_payloads.append(data)

    # Optional compatibility
    def receive(self, n: int) -> bytes:
        return b""


class TestPtpCartesianSequence(unittest.TestCase):
    def setUp(self):
        self.transport = DummyTransport()
        self.mc = MotionController(transport=self.transport)

    def test_load_all_points_csv(self):
        csv_path = PROJECT_ROOT / "points.csv"
        self.assertTrue(csv_path.exists(), f"CSV not found at {csv_path}")

        points = load_all_points_csv(str(csv_path))
        self.assertIsInstance(points, list)
        self.assertGreater(len(points), 0, "Expected at least one point in CSV")
        p0 = points[0]
        for attr in ("x", "y", "z", "a", "b", "c"):
            self.assertTrue(hasattr(p0, attr), f"Point missing attribute {attr}")

    def test_send_move_sequence_concatenated_xml(self):
        csv_path = PROJECT_ROOT / "points.csv"
        points = load_all_points_csv(str(csv_path))

        start_id = self.mc.cmd_counter
        self.mc._send_move_sequence(
            points=points,
            cmd_type=1,   # move
            mode=2,       # PTP Cartesian
            vel=0.2,
            base=0,
            tool=0,
            blending=0.0,
        )

        # Exactly one send with concatenated payload
        self.assertEqual(len(self.transport.sent_payloads), 1)
        payload = self.transport.sent_payloads[0]
        self.assertIsInstance(payload, (bytes, bytearray))
        text = payload.decode("utf-8", errors="ignore")

        # Expect one EthernetKRL block per point
        block_count = text.count("<EthernetKRL>")
        self.assertEqual(block_count, len(points))

        # IDs should increment by number of points
        self.assertEqual(self.mc.cmd_counter, start_id + len(points))

        # Sanity: a coordinate from first point should appear
        expected_x = str(points[0].x)
        self.assertIn(expected_x, text)


if __name__ == "__main__":
    unittest.main()
