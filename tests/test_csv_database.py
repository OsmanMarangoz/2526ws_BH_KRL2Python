import sys
import os
import unittest
from pathlib import Path

# Fügt den `src` Ordner in den Python-Pfad ein,
# damit wir die Klassen importieren können
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

from point import Point6D
from csvHelper import save_point_csv, load_point_csv, load_all_points_csv, init_csv

class TestCSVDatabase(unittest.TestCase):

    def setUp(self):
        # Wird VOR jedem einzelnen Test ausgeführt.
        # Wir definieren einen sicheren Test-Dateinamen,
        # damit wir nicht aus Versehen die echten Roboter-Punkte löschen!
        self.test_file = "test_points.csv"

    def tearDown(self):
        # Wird NACH jedem einzelnen Test ausgeführt.
        # löschen die Testdatei wieder, um keinen Müll zu hinterlassen.
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load_single_point(self):
        # 1. Dummy-Punkt erstellen
        p_in = Point6D(name="XP1", x=12.5, y=-5.0, z=500.2, a=90.0, b=0.0, c=-180.0)

        # 2. In die Test-CSV speichern
        save_point_csv(self.test_file, p_in)

        # 3. Wieder aus der CSV herausladen (Deserialisieren)
        p_out = load_point_csv(self.test_file, "XP1")

        # 4. Prüfen, ob die eingetragenen Werte 1:1 deckungsgleich mit den gelesenen sind
        self.assertEqual(p_in.name, p_out.name)
        self.assertEqual(p_in.x, p_out.x)
        self.assertEqual(p_in.y, p_out.y)
        self.assertEqual(p_in.a, p_out.a)

    def test_overwrite_existing_point(self):
        #speichern Punkt
        p1 = Point6D("Home", 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
        save_point_csv(self.test_file, p1)

        # überschreiben denselben Punkt mit NEUEN Werten
        p2_overwrite = Point6D("Home", 99.9, 50.0, 1.0, 0.0, 0.0, 0.0)
        save_point_csv(self.test_file, p2_overwrite, overwrite=True)

        # lesen ihn aus und erwarten die NEUEN Werte
        loaded = load_point_csv(self.test_file, "Home")
        self.assertEqual(loaded.x, 99.9, "Der X-Wert wurde nicht richtig überschrieben!")
        self.assertEqual(loaded.y, 50.0, "Der Y-Wert wurde nicht richtig überschrieben!")

    def test_no_overwrite_raises_error(self):
        # if overwrite=False, MUSS ein Fehler (ValueError) kommen
        p1 = Point6D("Home", 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
        save_point_csv(self.test_file, p1)

        # Versuche ihn ohne Erlaubnis zu überschreiben: Erwartung -> Exception
        with self.assertRaises(ValueError):
            save_point_csv(self.test_file, p1, overwrite=False)

    def test_load_all_points(self):
        # Speichere drei verschiedene Punkte in die CSV
        save_point_csv(self.test_file, Point6D("P1", 1, 2, 3, 0, 0, 0))
        save_point_csv(self.test_file, Point6D("P2", 4, 5, 6, 0, 0, 0))
        save_point_csv(self.test_file, Point6D("P3", 7, 8, 9, 0, 0, 0))

        # Alle auf einmal laden
        all_points = load_all_points_csv(self.test_file)

        # Erwartung: Es müssen genau 3 Punkte in der Liste sein
        self.assertEqual(len(all_points), 3)
        # Erwartung: Der Name des zweiten Punkts muss "P2" sein
        self.assertEqual(all_points[1].name, "P2")

    def test_point_not_found(self):
        # erstellen eine Datei und fügen P1 ein
        save_point_csv(self.test_file, Point6D("P1", 0,0,0,0,0,0))

        # suchen nach "Ghost" (existiert nicht in der CSV).
        # csvHelper soll KeyError werfen.
        with self.assertRaises(KeyError):
            load_point_csv(self.test_file, "Ghost")

if __name__ == '__main__':
    unittest.main()
