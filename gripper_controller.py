from transport import Transport

class GripperController:
    """
    Controller for KUKA gripper commands via EKI.

    Gripper Modes (from motion_eki.src):
        1 = Jaw Gripper
        2 = Vacuum Gripper

    Jaw DirectionMode:
        0 = Open
        1 = Close

    Command Type:
        3 = Grip only (no movement)
    """

    # Command type for grip-only commands
    COMMAND_TYPE_GRIP = 3

    # Gripper modes
    GRIP_MODE_JAW = 1
    GRIP_MODE_VACUUM = 2

    # Jaw direction modes
    JAW_DIRECTION_OPEN = 0
    JAW_DIRECTION_CLOSE = 1

    # Default jaw gripper values (adjust based on your hardware)
    DEFAULT_JAW_TOLERANCE = 50      # 0.5mm (value * 100)
    DEFAULT_JAW_VELOCITY = 50       # 50% speed
    DEFAULT_JAW_FORCE = 30          # grip force
    DEFAULT_JAW_BASE_POSITION = 75
    DEFAULT_JAW_WORK_POSITION = 4875
    DEFAULT_JAW_TEACH_POSITION = 3000
    DEFAULT_JAW_SHIFT_POSITION = 500

    def __init__(self, transport: Transport):
        self._transport = transport
        self._command_id = 0

    def _get_next_command_id(self) -> int:
        """Generate next command ID."""
        self._command_id += 1
        return self._command_id

    def _build_grip_command(
        self,
        grip_mode: int,
        jaw_tolerance: int = 0,
        jaw_velocity: int = 0,
        jaw_force: int = 0,
        jaw_base_position: int = 0,
        jaw_work_position: int = 0,
        jaw_teach_position: int = 0,
        jaw_shift_position: int = 0,
        jaw_direction_mode: int = 0,
        vacuum_suction: int = 0,
        vacuum_cylinder: float = 0.0
    ) -> str:
        """
        Build XML command string for gripper operation.

        Args:
            grip_mode: 1 = Jaw, 2 = Vacuum
            jaw_*: Jaw gripper parameters
            vacuum_*: Vacuum gripper parameters

        Returns:
            XML command string
        """
        command_id = self._get_next_command_id()

        xml = f'''<RobotCommand Id="{command_id}" Type="{self.COMMAND_TYPE_GRIP}">
    <Grip Mode="{grip_mode}">
        <Jaw Tolerance="{jaw_tolerance}" Velocity="{jaw_velocity}" Force="{jaw_force}" BasePosition="{jaw_base_position}" WorkPosition="{jaw_work_position}" TeachPosition="{jaw_teach_position}" ShiftPosition="{jaw_shift_position}" DirectionMode="{jaw_direction_mode}"/>
        <Vacuum Suction="{vacuum_suction}" Cylinder="{vacuum_cylinder}"/>
    </Grip>
</RobotCommand>'''

        return xml

    def jaw_open(
        self,
        velocity: int = None,
        force: int = None,
        tolerance: int = None,
        base_position: int = None,
        work_position: int = None,
        teach_position: int = None,
        shift_position: int = None
    ) -> None:
        """
        Open the jaw gripper.

        Args:
            velocity: Gripper speed (0-100%), default 50
            force: Grip force, default 30
            tolerance: Position tolerance, default 50 (0.5mm)
            base_position: Base position, default 75
            work_position: Work position, default 4875
            teach_position: Teach position, default 3000
            shift_position: Shift position, default 500
        """
        xml = self._build_grip_command(
            grip_mode=self.GRIP_MODE_JAW,
            jaw_tolerance=tolerance if tolerance is not None else self.DEFAULT_JAW_TOLERANCE,
            jaw_velocity=velocity if velocity is not None else self.DEFAULT_JAW_VELOCITY,
            jaw_force=force if force is not None else self.DEFAULT_JAW_FORCE,
            jaw_base_position=base_position if base_position is not None else self.DEFAULT_JAW_BASE_POSITION,
            jaw_work_position=work_position if work_position is not None else self.DEFAULT_JAW_WORK_POSITION,
            jaw_teach_position=teach_position if teach_position is not None else self.DEFAULT_JAW_TEACH_POSITION,
            jaw_shift_position=shift_position if shift_position is not None else self.DEFAULT_JAW_SHIFT_POSITION,
            jaw_direction_mode=self.JAW_DIRECTION_OPEN
        )

        self._transport.send(xml)
        print(f" Jaw gripper OPEN command sent (ID: {self._command_id})")

    def jaw_close(
        self,
        velocity: int = None,
        force: int = None,
        tolerance: int = None,
        base_position: int = None,
        work_position: int = None,
        teach_position: int = None,
        shift_position: int = None
    ) -> None:
        """
        Close the jaw gripper.

        Args:
            velocity: Gripper speed (0-100%), default 50
            force: Grip force, default 30
            tolerance: Position tolerance, default 50 (0.5mm)
            base_position: Base position, default 75
            work_position: Work position, default 4875
            teach_position: Teach position, default 3000
            shift_position: Shift position, default 500
        """
        xml = self._build_grip_command(
            grip_mode=self.GRIP_MODE_JAW,
            jaw_tolerance=tolerance if tolerance is not None else self.DEFAULT_JAW_TOLERANCE,
            jaw_velocity=velocity if velocity is not None else self.DEFAULT_JAW_VELOCITY,
            jaw_force=force if force is not None else self.DEFAULT_JAW_FORCE,
            jaw_base_position=base_position if base_position is not None else self.DEFAULT_JAW_BASE_POSITION,
            jaw_work_position=work_position if work_position is not None else self.DEFAULT_JAW_WORK_POSITION,
            jaw_teach_position=teach_position if teach_position is not None else self.DEFAULT_JAW_TEACH_POSITION,
            jaw_shift_position=shift_position if shift_position is not None else self.DEFAULT_JAW_SHIFT_POSITION,
            jaw_direction_mode=self.JAW_DIRECTION_CLOSE
        )

        self._transport.send(xml)
        print(f" Jaw gripper CLOSE command sent (ID: {self._command_id})")

    def vacuum_on(self, cylinder: float = 0.0) -> None:
        """
        Turn vacuum gripper ON.

        Args:
            cylinder: Cylinder position, default 0.0
        """
        xml = self._build_grip_command(
            grip_mode=self.GRIP_MODE_VACUUM,
            vacuum_suction=1,
            vacuum_cylinder=cylinder
        )

        self._transport.send(xml)
        print(f" Vacuum ON command sent (ID: {self._command_id})")

    def vacuum_off(self, cylinder: float = 0.0) -> None:
        """
        Turn vacuum gripper OFF.

        Args:
            cylinder: Cylinder position, default 0.0
        """
        xml = self._build_grip_command(
            grip_mode=self.GRIP_MODE_VACUUM,
            vacuum_suction=0,
            vacuum_cylinder=cylinder
        )

        self._transport.send(xml)
        print(f" Vacuum OFF command sent (ID: {self._command_id})")