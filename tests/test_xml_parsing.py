import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from motion_controller import MotionController
from point import Point6D, JointState

class TestXMLParsing(unittest.TestCase):

    @patch('motion_controller.p')
    def setUp(self, mock_pybullet):
        # Transport-Attrappe erstellen
        mock_transport = MagicMock()
        self.motion = MotionController(mock_transport)

    def test_get_current_Point6D_success(self):
        # 1. Simuliere ein perfektes XML vom KUKA Roboter
        simulated_kuka_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<RobotState>'
            '<Position>'
            '<Cartesian X="150.5" Y="-20.1" Z="330.0" A="90.0" B="0.0" C="180.0"/>'
            '</Position>'
            '</RobotState>'
        ).encode('utf-8')

        self.motion.lastMotionPacket = simulated_kuka_response

        # 2. Methode aufrufen
        result = self.motion.get_current_Point6D(name="MockPoint")

        # 3. Prüfen, ob die Koordinaten exakt gelesen wurden
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "MockPoint")
        self.assertEqual(result.x, 150.5)
        self.assertEqual(result.y, -20.1)
        self.assertEqual(result.z, 330.0)
        self.assertEqual(result.c, 180.0)

    def test_get_current_Point6D_missing_cartesian(self):
        # 1. Simuliere ungültiges XML (Cartesian Tag fehlt komplett)
        bad_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<RobotState><Position></Position></RobotState>'
        ).encode('utf-8')

        self.motion.lastMotionPacket = bad_response

        # 2. Code sollte den ValueError fangen und None ausgeben
        result = self.motion.get_current_Point6D(name="BadPoint")
        self.assertIsNone(result, "Ein fehlerhaftes XML sollte None zurückgeben anstatt abzustürzen!")

    def test_get_current_joint_state_success(self):
        # 1. Simuliere perfektes Joint-XML
        simulated_joint_response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<RobotState>'
            '<Position>'
            '<Joint A1="10.0" A2="-20.5" A3="30.0" A4="40.0" A5="50.0" A6="-60.0"/>'
            '</Position>'
            '</RobotState>'
        ).encode('utf-8')

        self.motion.lastMotionPacket = simulated_joint_response

        # 2. Ausführen
        result = self.motion.get_current_joint_state()

        # 3. Prüfen
        self.assertIsNotNone(result)
        self.assertEqual(result.a1, 10.0)
        self.assertEqual(result.a2, -20.5)
        self.assertEqual(result.a6, -60.0)

    def test_update_command_state(self):
        # 1. Wir tun so, als ob der Roboter sagt, er hat Befehl 42 beendet
        response = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<RobotState>'
            '<Command Finished_Id="42"/>'
            '</RobotState>'
        ).encode('utf-8')

        self.motion.lastMotionPacket = response

        # 2. Methode ausführen, die intern "last_finished_id" aktualisiert
        self.motion._update_command_state()

        # 3. State prüfen
        self.assertEqual(self.motion.last_finished_id, 42, "Die ID 42 wurde nicht aus dem XML übernommen")


if __name__ == '__main__':
    unittest.main()
