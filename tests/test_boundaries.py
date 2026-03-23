import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Fügt den `src` Ordner in den Python-Pfad ein
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from motion_controller import MotionController
from meta_controller import MetaController

class TestBoundaries(unittest.TestCase):

    @patch('motion_controller.p')
    def setUp(self, mock_pybullet):
        mock_transport = MagicMock()
        self.motion = MotionController(mock_transport)
        self.meta = MetaController(mock_transport)

    def test_velocity_boundaries(self):
        # 1. Zu hoch (Limit laut Code ist 10.0)
        self.motion.set_default_velocity(150.0)
        self.assertEqual(self.motion.default_velocity, 10.0, "Velocity wurde nicht bei 10.0 gedeckelt!")

        # 2. Zu niedrig (Limit laut Code ist 0.0)
        self.motion.set_default_velocity(-5.5)
        self.assertEqual(self.motion.default_velocity, 0.0, "Velocity wurde nicht auf 0.0 angehoben!")

        # 3. Mitten drin (Normaler Wert)
        self.motion.set_default_velocity(2.5)
        self.assertEqual(self.motion.default_velocity, 2.5)

    def test_meta_override_boundaries(self):
        # 1. Zu hoch (Override über 100% macht keinen Sinn)
        self.meta.set_override(150)

        # Wir prüfen mit welchem Parameter _build_xml intern aufgerufen wurde.
        # Im meta_controller.py hast du programmiert: value = max(0, min(100, value))
        # Da wir mocken mussten wir nicht viel tun, wir prüfen nur den gesendeten XML

        # Wir können das Transport-Mock checken
        last_call = self.meta.metaTransport.send.call_args[0][0].decode('utf-8')
        self.assertIn('VelocityOverride="100"', last_call, "Override wurde nicht auf 100 begrenzt!")

        # 2. Zu niedrig
        self.meta.set_override(-50)
        last_call_neg = self.meta.metaTransport.send.call_args[0][0].decode('utf-8')
        self.assertIn('VelocityOverride="0"', last_call_neg, "Override wurde nicht auf 0 begrenzt!")

    def test_move_sequence_empty_list(self):
        # Testet den Edge-case: Was ist, wenn wir dem Roboter eine leere Sequenz senden?
        # Erwartung: "No points provided for sequence." wird geprintet und Methode returned None,
        # ohne dass versucht wird, ein leeres XML zu schicken.

        # Senden eines leeren Arrays
        self.motion.move_sequence(points=[], mode=2)

        # Transport.send darf NIEMALS aufgerufen worden sein!
        self.motion.motionTransport.send.assert_not_called()

if __name__ == '__main__':
    unittest.main()
