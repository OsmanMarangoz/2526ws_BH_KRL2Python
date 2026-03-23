import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch
from pathlib import Path

# Fügt den `src` Ordner in den Python-Pfad ein,
# damit wir die Klassen importieren können
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from motion_controller import MotionController
from meta_controller import MetaController
from point import Point6D

# Wir "patchen" (überschreiben) PyBullet, damit beim Starten der
# Tests KEIN echtes grafisches Simulationsfenster im Hintergrund aufspringt.
class TestXMLGeneration(unittest.TestCase):

    @patch('motion_controller.p')
    def setUp(self, mock_pybullet):
        # Wir geben einen komplett falschen, stummen Transport-Layer mit.
        # So versuchen die Controller gar nicht erst, eine Netzwerkverbindung aufzubauen.
        mock_transport = MagicMock()

        self.motion = MotionController(mock_transport)
        self.meta = MetaController(mock_transport)

    def test_build_move_xml(self):
        # 1. Test-Daten vorbereiten
        pt = Point6D("P_Test", x=100.5, y=-50.2, z=300.0, a=90.0, b=0.0, c=180.0)

        # 2. Die XML-Makers Funktion aufrufen
        xml_bytes = self.motion._build_move_xml(
            cmd_id=42, point=pt, cmd_type=1, mode=2,
            vel=0.5, acc=1.0, base=0, tool=1, blending=0.0
        )

        # 3. Den Byte-String in einen normalen String umwandeln
        xml_str = xml_bytes.decode('utf-8')

        # 4. Grundlegende Formatierungs-Checks
        self.assertTrue(xml_str.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))
        self.assertIn('<EthernetKRL>', xml_str)

        # 5. Echter, robuster Check: Ist das generierte XML gültig (parse-bar)?
        root = ET.fromstring(xml_str)

        # Suchen wir das RobotCommand Element
        cmd_element = root.find('.//RobotCommand')
        self.assertIsNotNone(cmd_element, "Element 'RobotCommand' fehlt!")
        self.assertEqual(cmd_element.attrib['Id'], '42', "'Id' wurde nicht richtig gesetzt")

        # Prüfen wir, ob die Koordinaten auch korrekt in das XML eingeflossen sind!
        cart_element = root.find('.//Cartesian')
        self.assertIsNotNone(cart_element, "Element 'Cartesian' fehlt!")
        self.assertEqual(cart_element.attrib['X'], '100.5')
        self.assertEqual(cart_element.attrib['Y'], '-50.2')
        self.assertEqual(cart_element.attrib['C'], '180.0')

    def test_build_grip_xml(self):
        # In deinem Code liest der Gripper stattdessen immer self.cmd_counter aus
        self.motion.cmd_counter = 77

        # Richtungscode 1 (Jaw Close)
        xml_bytes = self.motion._build_grip_xml(jaw_direction_mode=1)
        root = ET.fromstring(xml_bytes.decode('utf-8'))

        cmd_element = root.find('.//RobotCommand')
        self.assertEqual(cmd_element.attrib['Id'], '77')
        self.assertEqual(cmd_element.attrib['Type'], '3')

        jaw_element = root.find('.//Jaw')
        self.assertIsNotNone(jaw_element)
        self.assertEqual(jaw_element.attrib['DirectionMode'], '1')

    def test_build_meta_xml(self):
        # Metacontroller Override Kommando Testen
        xml_bytes = self.meta._build_xml(override=50, abort=0)
        xml_str = xml_bytes.decode('utf-8')
        root = ET.fromstring(xml_str)

        meta_cmd = root.find('.//MetaCommand')
        self.assertIsNotNone(meta_cmd)
        self.assertEqual(meta_cmd.attrib['VelocityOverride'], '50')
        self.assertEqual(meta_cmd.attrib['AbortCommand'], '0')

if __name__ == '__main__':
    unittest.main()
