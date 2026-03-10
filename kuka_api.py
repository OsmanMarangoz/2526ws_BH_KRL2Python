"""
High-level scripting API for KUKA robot control.

This module wraps the Robot class to provide a simple, user-friendly
interface for writing robot programs as Python scripts — no interactive
input required.

Example usage:
    from kuka_api import KukaRobot, Point6D

    robot = KukaRobot("10.181.116.41")
    robot.connect()

    robot.set_velocity(0.3)
    robot.ptp(100, 200, 300, 0, 90, 0)
    robot.gripper_open()
    robot.ptp("my_saved_point")
    robot.gripper_close()

    # robot.disconnect()  # nur wenn gewünscht
"""

import threading
import time
from robot import Robot
from point import Point6D
from csvHelper import load_point_csv, load_all_points_csv, save_point_csv


class KukaRobot:
    """
    High-level scripting interface for KUKA robot control.

    Can be used as a context manager (with-statement) or manually
    via connect() / disconnect().
    """

    DEFAULT_PORT_META = 54601
    DEFAULT_PORT_MOTION = 54602

    def __init__(self, ip: str,
                 port_meta: int = DEFAULT_PORT_META,
                 port_motion: int = DEFAULT_PORT_MOTION,
                 csv_file: str = "points.csv"):
        """
        Initialize the KUKA robot connection parameters.

        Args:
            ip: IP address of the KUKA controller.
            port_meta: TCP port for meta commands (override, e-stop).
            port_motion: TCP port for motion commands.
            csv_file: Default CSV file for loading/saving points.
        """
        self._robot = Robot(ip, port_meta, port_motion)
        self._csv_file = csv_file

        # Default motion parameters
        self._velocity: float = 0.2
        self._acceleration: float = 0.2
        self._blending: float = 0.0
        self._tool: int = 0
        self._base: int = 0

        self._meta_thread: threading.Thread | None = None
        self._connected = False

    # ------------------------------------------------------------------ #
    #  Connection management                                              #
    # ------------------------------------------------------------------ #

    def connect(self):
        """Connect to the KUKA controller and start background threads."""
        self._robot.connect()
        self._connected = True

        # Thread 1: Meta-receive loop (override / e-stop feedback)
        self._meta_thread = threading.Thread(
            target=self._robot.receive_meta_loop,
            daemon=True,
        )
        self._meta_thread.start()

        # Thread 2: Motion visualization (receives actual robot position)
        self._motion_thread = threading.Thread(
            target=self._robot.motion_visualization_loop,
            daemon=True,
        )
        self._motion_thread.start()

        print(f"[KukaRobot] Connected to {self._robot.motion_transport.ip}")

    def disconnect(self):
        """Disconnect from the KUKA controller. Call this only when you explicitly want to close the connection."""
        if self._connected:
            self._robot.disconnect()
            self._connected = False
            print("[KukaRobot] Disconnected")

    # ------------------------------------------------------------------ #
    #  Settings                                                           #
    # ------------------------------------------------------------------ #

    def set_velocity(self, vel: float):
        """Set the default velocity for subsequent moves (0.0 – 10.0)."""
        self._velocity = max(0.0, min(vel, 10.0))

    def set_acceleration(self, acc: float):
        """Set the default acceleration for subsequent moves."""
        self._acceleration = acc

    def set_blending(self, blending: float):
        """Set the default blending radius for subsequent moves."""
        self._blending = blending

    def set_tool(self, tool: int):
        """Set the active tool index."""
        self._tool = tool

    def set_base(self, base: int):
        """Set the active base index."""
        self._base = base

    def set_override(self, percent: int):
        """Set the velocity override (0 – 100 %)."""
        self._robot.set_override(percent)
    @property
    def cmd_counter(self) -> int:
        """The next command ID that will be sent."""
        return self._robot.cmd_counter

    @property
    def last_finished_id(self) -> int:
        """The last command ID the robot reported as finished."""
        return self._robot.last_finished_id

    # ------------------------------------------------------------------ #
    #  Point helpers                                                      #
    # ------------------------------------------------------------------ #

    def point(self, x: float, y: float, z: float,
              a: float, b: float, c: float,
              name: str = "script_point") -> Point6D:
        """Create a Point6D from coordinates."""
        return Point6D(name=name, x=x, y=y, z=z, a=a, b=b, c=c)

    def load_point(self, name: str, csv_file: str | None = None) -> Point6D:
        """Load a named point from a CSV file."""
        return load_point_csv(csv_file or self._csv_file, name)

    def load_all_points(self, csv_file: str | None = None) -> list[Point6D]:
        """Load all points from a CSV file."""
        return load_all_points_csv(csv_file or self._csv_file)

    def save_point(self, name: str, x: float, y: float, z: float,
                   a: float, b: float, c: float,
                   csv_file: str | None = None):
        """Save a point to a CSV file."""
        pt = Point6D(name=name, x=x, y=y, z=z, a=a, b=b, c=c)
        save_point_csv(csv_file or self._csv_file, pt, overwrite=True)

    # ------------------------------------------------------------------ #
    #  Resolving targets                                                  #
    # ------------------------------------------------------------------ #

    def _resolve_target(self, target, name: str = "script_point") -> Point6D:
        """
        Flexibly resolve a move target to a Point6D.

        Accepted forms:
          - Point6D instance             → used as-is
          - str                          → looked up from CSV by name
          - tuple/list of 6 floats       → (x, y, z, a, b, c)
        """
        if isinstance(target, Point6D):
            return target
        if isinstance(target, str):
            return self.load_point(target)
        if isinstance(target, (tuple, list)) and len(target) == 6:
            return Point6D(name=name, x=target[0], y=target[1], z=target[2],
                           a=target[3], b=target[4], c=target[5])
        raise TypeError(
            f"Invalid target type: {type(target)}. "
            "Pass a Point6D, a point name (str), or a tuple of 6 floats."
        )

    # ------------------------------------------------------------------ #
    #  Motion commands                                                    #
    # ------------------------------------------------------------------ #

    def ptp(self, *args, vel: float | None = None,
            base: int | None = None, tool: int | None = None,
            blending: float | None = None):
        """
        PTP (point-to-point) Cartesian move.

        Usage:
            robot.ptp(x, y, z, a, b, c)          # six floats
            robot.ptp((x, y, z, a, b, c))         # tuple
            robot.ptp("my_saved_point")            # CSV point name
            robot.ptp(my_point6d)                  # Point6D object
            robot.ptp(x, y, z, a, b, c, vel=0.5)  # with explicit velocity
        """
        target = self._unpack_args(args)
        pt = self._resolve_target(target)
        self._robot.ptp(
            point=pt,
            vel=vel if vel is not None else self._velocity,
            base=base if base is not None else self._base,
            tool=tool if tool is not None else self._tool,
            blending=blending if blending is not None else self._blending,
        )

    def lin(self, *args, vel: float | None = None,
            base: int | None = None, tool: int | None = None,
            blending: float | None = None):
        """
        LIN (linear) Cartesian move.

        Same argument forms as ptp().
        """
        target = self._unpack_args(args)
        pt = self._resolve_target(target)
        self._robot.lin(
            point=pt,
            vel=vel if vel is not None else self._velocity,
            base=base if base is not None else self._base,
            tool=tool if tool is not None else self._tool,
            blending=blending if blending is not None else self._blending,
        )

    def circ(self, *args, vel: float | None = None,
             base: int | None = None, tool: int | None = None,
             blending: float | None = None):
        """
        CIRC (circular) Cartesian move.

        Same argument forms as ptp().
        """
        target = self._unpack_args(args)
        pt = self._resolve_target(target)
        self._robot.circ(
            point=pt,
            vel=vel if vel is not None else self._velocity,
            base=base if base is not None else self._base,
            tool=tool if tool is not None else self._tool,
            blending=blending if blending is not None else self._blending,
        )

    def move_sequence(self, points: list, mode: str = "ptp",
                      vel: float | None = None,
                      base: int | None = None, tool: int | None = None,
                      blending: float | None = None):
        """
        Send a sequence of moves in a single transmission.

        Args:
            points: List of targets (Point6D, str names, or coordinate tuples).
            mode: "ptp", "lin", or "circ".
            vel, base, tool, blending: overrides (or uses defaults).
        """
        mode_map = {"ptp": 2, "lin": 3, "circ": 4}
        mode_int = mode_map.get(mode.lower())
        if mode_int is None:
            raise ValueError(f"Unknown mode '{mode}'. Use 'ptp', 'lin', or 'circ'.")

        resolved = [self._resolve_target(p) for p in points]
        self._robot._send_move_sequence(
            points=resolved,
            cmd_type=1,
            mode=mode_int,
            vel=vel if vel is not None else self._velocity,
            base=base if base is not None else self._base,
            tool=tool if tool is not None else self._tool,
            blending=blending if blending is not None else self._blending,
        )

    def move_sequence_from_csv(self, csv_file: str, mode: str = "ptp",
                               vel: float | None = None,
                               base: int | None = None, tool: int | None = None,
                               blending: float | None = None):
        """
        Load all points from a CSV file and send them as a move sequence.

        This is the scripting equivalent of the interactive 'Move in Sequence'
        menu in command.py.

        Args:
            csv_file: Path to the CSV file (e.g. "sequence_points.csv").
            mode: "ptp", "lin", or "circ".
            vel, base, tool, blending: overrides (or uses defaults).
        """
        points = load_all_points_csv(csv_file)
        if not points:
            print(f"[KukaRobot] ERROR: No points found in '{csv_file}'.")
            return
        print(f"[KukaRobot] Loaded {len(points)} points from '{csv_file}'.")
        self.move_sequence(points, mode=mode, vel=vel, base=base, tool=tool, blending=blending)

    # ------------------------------------------------------------------ #
    #  Gripper commands                                                   #
    # ------------------------------------------------------------------ #

    def gripper_open(self):
        """Open the jaw gripper."""
        self._robot.jaw_open()

    def gripper_close(self):
        """Close the jaw gripper."""
        self._robot.jaw_close()

    # ------------------------------------------------------------------ #
    #  Safety commands                                                    #
    # ------------------------------------------------------------------ #

    def emergency_stop(self):
        """Trigger an emergency stop."""
        self._robot.emergency_stop()

    def reset(self):
        """Reset after an emergency stop / abort."""
        self._robot.reset_abort()

    # ------------------------------------------------------------------ #
    #  Sleep / wait helper                                                #
    # ------------------------------------------------------------------ #

    def wait(self, seconds: float):
        """Pause script execution for the given number of seconds."""
        time.sleep(seconds)

    def keep_alive(self):
        """Block the main thread to keep the connection open.

        Without this, the Python process exits after the last command
        and the OS closes all sockets — causing an unintended disconnect.

        Call this at the end of your script if you want the connection
        to stay open. Press Ctrl+C to stop.
        """
        print("[KukaRobot] Keeping connection alive. Press Ctrl+C to stop.")
        try:
            while self._connected:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[KukaRobot] Stopped by user.")

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _unpack_args(args):
        """
        Normalize variadic args into a single target value.

        - 6 floats  → tuple
        - 1 arg     → pass through (Point6D / str / tuple)
        """
        if len(args) == 6:
            return tuple(args)
        if len(args) == 1:
            return args[0]
        raise TypeError(
            f"Expected 1 target or 6 coordinate values, got {len(args)} arguments."
        )
