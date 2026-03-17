KRL2Python — Abschlussdokumentation

Dieses Repository enthält ein schlankes Python-Framework zur Kommunikation mit einem KUKA-Roboter über die EthernetKRL-Schnittstelle. Es ermöglicht das Senden von Bewegungs- und Meta-Kommandos, das Speichern und Laden von kartesischen Punkten via CSV und eine einfache lokale Visualisierung der Gelenkwinkel mit PyBullet.

**Kurz:** Python-Client + einfache CLI zur Steuerung und Visualisierung von KRL-Bewegungen.

**Inhalt dieser Dokumentation:** Voraussetzungen, Installation, Architekturübersicht, Klassenbeschreibung und Beispielanwendung.

**Projektdateien (Auswahl):**
- **Main:** [Main.py](Main.py)
- **Beispielskript:** [example_script.py](example_script.py)
- **Robot/Controller:** [robot.py](robot.py), [motion_controller.py](motion_controller.py), [meta_controller.py](meta_controller.py)
- **Kommunikation:** [transport.py](transport.py)
- **CLI / Bedienlogik:** [command.py](command.py)
- **Hilfsfunktionen (CSV / Punkte):** [csvHelper.py](csvHelper.py), [point.py](point.py)
- **Punkte-CSV:** [points.csv](points.csv), [sequence_points.csv](sequence_points.csv)

**Hinweis:** Diese README beschreibt, wie Sie das Projekt lokal betreiben und (sofern vorhanden) mit einem KUKA-Controller über EthernetKRL verbinden.

**Voraussetzungen**
- **Python:** Version 3.10 oder neuer (benötigt `match/case` und moderne Typ-Annotationen).
- **Benötigte Python-Pakete:** `pybullet`, `keyboard`. Die Standardbibliothek (z. B. `csv`, `xml`, `socket`, `pathlib`, `time`) wird verwendet.
- **Optional / Für echten Roboterbetrieb:** KUKA-Roboter mit aktivierter EthernetKRL-Schnittstelle, passende Ports (siehe Abschnitt Anwendung). Zur Simulation: PyBullet ist bereits integriert.

Installationsschritte (Beispiel mit pip):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pybullet keyboard
```

Falls Sie Conda verwenden (wie in der Entwicklungsumgebung):

```bash
conda create -n kuka-python python=3.11 -y
conda activate kuka-python
pip install pybullet keyboard
```

**Architektur (High-Level)**
- **Transport-Schicht:** `transport.py` implementiert `TcpTransport` und kapselt Raw-TCP-Verbindungen zum Roboter (connect/disconnect/send/receive).
- **Motion / Meta Controller:**
  - `motion_controller.py` enthält `MotionController`: baut XML-EthernetKRL-Move-Nachrichten, sendet Bewegungen, parst eingehende `RobotState`-Pakete und bietet eine PyBullet-Visualisierung der Gelenkwinkel.
  - `meta_controller.py` enthält `MetaController`: sendet Meta-Kommandos wie Velocity Override oder Abort.
- **Robot-Klasse:** `robot.py` kombiniert `MotionController` und `MetaController` (Mehrfachvererbung) und hält zwei `TcpTransport`-Instanzen (meta + motion).
- **CLI / Bedienung:** `command.py` bietet ein textbasiertes Menü zum Auswählen von Modi (Move, Grip, SavePoint, Settings) und startet Threads für Safety-Hotkeys und Bedienlogik.
- **Daten & Hilfsfunktionen:** `csvHelper.py` zum Lesen/Schreiben von Punkt-CSV-Dateien; `point.py` definiert `Point6D` und `JointState`.

**Schema / Kommunikationsfluss**
- CLI (`command.py`) ↔ Robot (`robot.py`) ↔ Transport (`transport.py`) ↔ Robotercontroller (EthernetKRL)
- Motion-Transport und Meta-Transport sind getrennt, übliche Ports werden in Beispielen benutzt (siehe `Main.py`).

**Klassen & Module (Kurzbeschreibung)**
- **`Point6D`, `JointState`** (`point.py`): Dataclasses für kartesische Punkte (X,Y,Z,A,B,C) und Gelenkzustände.
- **`TcpTransport`** (`transport.py`): Einfacher TCP-Wrapper. Methoden: `connect()`, `disconnect()`, `send(data)`, `receive()`.
- **`MotionController`** (`motion_controller.py`): Aufbau von Move-/Grip-/Sequence-XML-Nachrichten, Methoden: `ptp`, `lin`, `circ`, `ptp_joint`, `move_sequence`, `touchup`, plus `motion_visualization_loop()` für PyBullet.
- **`MetaController`** (`meta_controller.py`): Methoden `set_override(value)` und `abort()`; baut Meta-XML.
- **`Robot`** (`robot.py`): Kombiniert Motion+Meta Controller; verwaltet `TcpTransport`-Instanzen und Threads (Empfang/Visualisierung).
- **`Command`** (`command.py`): Interaktive Steuerung (Menüs) und Hilfsfunktionen zum Laden/Speichern von Punkten (`csvHelper.py`). Startet Safety- und Motion-Threads.
- **`csvHelper`** (`csvHelper.py`): CSV-Header: `name,x,y,z,a,b,c`. Funktionen: `init_csv`, `save_point_csv`, `load_point_csv`, `load_all_points_csv`.

**Konfiguration & typische Werte**
- Standard-IP/Ports (Beispiel in `Main.py` und `example_script.py`):
  - IP: `10.181.116.51`
  - Meta-Port: `54601`
  - Motion-Port: `54602`

Passen Sie diese Werte in `Main.py` oder in Ihrem Startskript an die Adresse Ihres KUKA-Controllers an.

**CSV-Format**
- Header (erste Zeile): `name,x,y,z,a,b,c`
- Beispielzeile: `Home,0,0,100,0,0,0`
- `sequence_points.csv` kann verwendet werden, um mehrere Punkte in einer Übertragung zu senden.

**KRL / Roboter-Integration**
- Das Projekt sendet EthernetKRL-XML-Nachrichten. Damit der Roboter sie akzeptiert, muss auf dem KUKA-Controller die EthernetKRL-Schnittstelle aktiviert sein (KRC-Konfiguration / KUKA.OfficeLite oder passendes KRL-Setup).
- Prüfungen vor dem Einsatz auf einem echten Roboter:
  - Sicherheit: Arbeitsraum sichern, Not-Aus testen.
  - Velocity/Acceleration prüfen (Default-Werte in `MotionController` sind konservativ einstellbar).
  - Testen zunächst in Simulation (PyBullet) oder auf einem Offline-Controller (OfficeLite / Simulationstool).

**Beispiel: Ablauf zum Starten**
1. virtuelle Umgebung aktivieren und Abhängigkeiten installieren (siehe oben).
2. In `Main.py` IP und Ports anpassen.
3. `python Main.py` starten. Das Menü ermöglicht interaktives Steuern.

Beispiel für nicht-interaktives Skript siehe [example_script.py](example_script.py).

**Tipps zur Fehlersuche**
- Wenn `TcpTransport.connect()` fehlschlägt: Prüfen Sie Netzwerkverbindung / IP / Port und Firewall.
- Bei XML-Parse-Fehlern: Prüfen Sie, ob empfangene Paketgrenzen korrekt sind (der Code beschneidet empfangene Bytes bis `</RobotState>`).
- PyBullet zeigt die Gelenkstellung an; falls kein GUI erscheint, prüfen Sie, ob X-Display (Linux) verfügbar ist oder verwenden Sie `pybullet.DIRECT` für headless.

**Erweiterungsmöglichkeiten**
- Implementieren einer robusteren Nachrichten-Frame-Logik (z. B. Paket-Assembler für Fragmentierung).
- Integration eines Logging-Backends statt `print()`.
- Unterstützung weiterer KUKA-Funktionen (I/O, Trajektorie-Feedback).

**Quellen / Dateien**
- Hauptskript: [Main.py](Main.py)
- Bedienlogik: [command.py](command.py)
- Robotik-Logik: [robot.py](robot.py), [motion_controller.py](motion_controller.py), [meta_controller.py](meta_controller.py)
- Transport: [transport.py](transport.py)
- Punkte / CSV: [point.py](point.py), [csvHelper.py](csvHelper.py), [points.csv](points.csv), [sequence_points.csv](sequence_points.csv)

Wenn Sie wollen, kann ich nun ein `requirements.txt` hinzufügen, oder die README ins Englische übersetzen. Was soll ich als Nächstes tun?
# 2526ws_BH_KRL2Python
