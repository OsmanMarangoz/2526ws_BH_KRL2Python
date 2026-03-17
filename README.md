# Tutorial to set up KUKA KR3 for 2526ws_BH_KRL2Python
> [!NOTE]
> Dieses Projekt steuert einen KUKA-Roboter aus Python über zwei TCP-Kanäle (Motion + Meta) und visualisiert die Gelenkzustände in PyBullet.

> [!NOTE]
> Das Repository ist für einen KR3 R540 vorkonfiguriert und kann durch Anpassung von IP-Adressen, Ports und Punktdaten auf andere Setups übertragen werden.

---

## Voraussetzungen
- Python 3.10 oder neuer
- Conda (Miniconda oder Anaconda)
- Netzwerkzugriff auf den KUKA Controller
- GUI/OpenGL-Unterstützung (für PyBullet)

---

## Einrichtung – Python Umgebung

### 1. Repository klonen
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Conda Environment erstellen
```bash
conda create -n kuka_env python=3.10
conda activate kuka_env
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. ggf. PyBullet überprüfen - tbd

---

## Einrichtung - Netzwerkkonfiguration
Vor dem ersten Start müssen die Verbindungsparameter zum Roboter überprüft und ggf. angepasst werden.

### 1. Relevante Dateien
Überprüfe die Verbindungseinstellungen in folgenden Dateien:
- `src/Main.py`
- `scripts/example_script.py`
  
### 2. Standardwerte im Projekt
Dieses Projekt verwendet standardmäßig folgende Konfiguration:
- Robot IP: `10.181.116.51`
- Meta Port: `54601`
- Motion Port: `54602`
  
### 3. Anpassung der Parameter
Falls dein Roboter oder Netzwerk davon abweicht, müssen IP-Adresse und Ports entsprechend angepasst werden.
In den oben genannten Dateien:

```python
ROBOT_IP = "10.xxx.xxx.xxx"
META_PORT = XXXX
MOTION_PORT = XXXX
```
- **ROBOT_IP** → IP-Adresse des KUKA Controllers  
- **META_PORT** → Port für Meta-Kommunikation  
- **MOTION_PORT** → Port für Motion-Kommunikation/ Bewegungsbefehle  

> ⚠️ Die Portnummern müssen mit der Konfiguration auf der KUKA-Seite übereinstimmen.

### 4. IP-Konfiguration im Roboternetzwerk
Damit die Kommunikation funktioniert, müssen sich **Roboter und Laptop im selben Netzwerk (Subnetz)** befinden.
- Der Roboter besitzt eine feste IP-Adresse (z. B. `10.181.116.51`)
- Der Laptop muss eine freie IP-Adresse im gleichen Netzwerk erhalten

#### Beispiel:

| Gerät    | IP-Adresse        |
|----------|------------------|
| Roboter  | 10.181.116.51    |
| Laptop   | 10.181.116.100   |

> ⚠️ Wichtig:
> - Die ersten drei Blöcke müssen identisch sein (z. B. `10.181.116.xxx` bei Subnetzmaske 255.255.255.0)
> - Die gewählte IP darf noch nicht im Netzwerk verwendet werden

### 5. Verbindung testen
Um sicherzustellen, dass die Netzwerkverbindung zum Roboter funktioniert, kann dieser vorab angepingt werden:
```bash
ping 10.181.116.51
```

### 6. Erwartetes Ergebnis
- Der Roboter antwortet auf die Anfrage
- Keine Paketverluste

Beispiel:
```bash
64 bytes from 10.181.116.51: icmp_seq=1 ttl=64 time=0.5 ms
```

---

### Hinweis
- Wenn keine Antwort kommt:
  - IP-Adresse überprüfen
  - Laptop im richtigen Netzwerk?
  - Freie IP-Adresse gewählt?
  - Netzwerkkabel verbunden?

> ⚠️ Der Ping-Test bestätigt nur die grundlegende Netzwerkverbindung.  
> Für die Steuerung müssen zusätzlich die richtigen Ports gesetzt und die EKI-Schnittstelle auf dem Roboter aktiv sein.


## Einrichtung – Kuka Robot Control (KRC)
1. Power and boot the robot/controller.
2. Ensure the robot-side program that serves Ethernet/TCP commands is running.
3. Confirm that both motion and meta interfaces are active on the controller.
4. Check that your Ubuntu PC can reach the robot IP (same subnet, no firewall block on required ports).

## Start Python Side on Ubuntu PC

### Interactive mode

```bash
python src/Main.py
```

This starts:
- TCP connection to motion + meta channels
- receive/visualization thread
- command menu (`MOVE`, `GRIP`, `SAVEPOINT`, `SETTINGS`)

### Scripted demo mode

```bash
python scripts/example_script.py
```

This executes a predefined pick/place sequence using points from `database/points.csv` and `database/sequence_points.csv`.

## Repository Layout

- `src/`
	- `Main.py` — interactive launcher
	- `command.py` — CLI + user workflows
	- `robot.py` — combines motion/meta controllers
	- `motion_controller.py` — move/gripper XML + PyBullet update loop
	- `meta_controller.py` — override + abort commands
	- `transport.py` — TCP socket transport
	- `csvHelper.py` — CSV read/write utilities
	- `point.py` — `Point6D`, `JointState`
- `database/`
	- `points.csv` — named poses
	- `sequence_points.csv` — sequence poses
- `kuka_kr3_support/`
	- URDF and meshes for KR3 visualization
- `scripts/`
	- runnable examples

## CSV Point Format

CSV header:

```text
name,x,y,z,a,b,c
```

Use cases:
- Save current pose (`touchup`)
- Save manual pose
- Load a named pose
- Load all points and run sequence (`PTP` or `LIN`)

## EKI/TCP Connection Notes

To avoid stale connections:

1. Stop the Python client first.
2. Then stop/deselect robot-side interface program(s).
3. Restart robot-side program(s) before reconnecting if needed.

This helps ensure clean reconnection on both motion and meta sockets.

## Troubleshooting

### 1) Linux keyboard hook error

If you see:

`ImportError: You must be root to use this library on linux.`

it comes from global hotkeys in `command.py` (`s`, `+`, `-`) using `keyboard`.

Options:
- run with sufficient privileges,
- or disable/remove hotkeys in `safetyLoop()` for non-root usage.

### 2) PyBullet URDF warnings

Warnings like `No inertial data for link...` are common with simplified URDFs and usually non-blocking.

### 3) No visualization window

`motion_controller.py` uses `p.connect(p.GUI)`. Ensure X11/desktop/OpenGL is available.

### 4) Socket timeout messages

Short timeouts are expected in polling loops. Persistent timeouts usually indicate network/interface mismatch.
