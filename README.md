# Tutorial to set up KUKA KR3 for 2526ws_BH_KRL2Python

> [!NOTE]
> This project controls a KUKA robot from Python via two TCP channels (motion + meta) and visualizes joint states in PyBullet.

> [!NOTE]
> The repository is configured for a KR3 R540 setup and can be adapted to other KUKA setups by changing IP/ports and point data.

## First Time Setup - Ubuntu PC

1. Clone this repository and open it in VS Code.
2. Ensure Python 3.10+ is available.
3. Install dependencies:

	 ```bash
	 python -m pip install pybullet keyboard
	 ```

4. Verify that the machine has GUI/OpenGL access (PyBullet uses GUI mode).
5. Connect the Ubuntu PC to the robot network.
6. Configure your network interface with a compatible static IP in the robot subnet.

## First Time Setup - Project Configuration

1. Check robot connection constants in:
	 - `src/Main.py`
	 - `scripts/example_script.py`
	 - `scripts/example_script copy.py`
2. Default values in this project are:
	 - Robot IP: `10.181.116.51`
	 - Meta port: `54601`
	 - Motion port: `54602`
3. If your robot/controller differs, update these constants before running.

## Start Hardware Interface on Robot

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
