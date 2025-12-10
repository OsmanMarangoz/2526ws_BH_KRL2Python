# import keyboard
from unittest import case
import keyboard
from point import Point6D
from robot import Robot
from csvHelper import load_point_csv,save_point_csv

from commandMode import CommandMode

class Command:

    def __init__(self, robot):
        self.robot = robot
        self.commandMode = CommandMode.CHANGEMODE      # Startmode
        # Globale Command-Parameter
        self.override = 1
        self.tool = 0
        self.base = 0
        self.velocity = 0.2
        self.acceleration = 0.2
        self.blending = 0.0
        self.fileName = "points.csv"

        # Gripper parameters (defaults)
        self.jaw_velocity = 50       # 0-100%
        self.jaw_force = 30
        self.jaw_tolerance = 50      # 0.5mm
        self.jaw_base_position = 75
        self.jaw_work_position = 4875
        self.jaw_teach_position = 3000
        self.jaw_shift_position = 500

# ------------------------------------------- Loops for threading -------------------------------------------
    def loop(self):
        while self.robot.motion_transport.connected:
            match self.commandMode:
                case CommandMode.CHANGEMODE:
                    self.changeMode()
                case CommandMode.MOVE:
                    self.move()
                case CommandMode.GRIP:
                    self.grip()
                case CommandMode.SAVEPOINT:
                    self.savePoint()
                case CommandMode.SETTINGS:
                    self.settings()
        print("Connection lost")

    def safetyLoop(self):
        keyboard.add_hotkey(",", lambda: self.robot.emergency_stop())
        keyboard.add_hotkey("e", lambda: self.robot.reset_abort())
        keyboard.add_hotkey("+", lambda: self.setOverride(self.override + 0.1))
        keyboard.add_hotkey("-", lambda: self.setOverride(self.override - 0.1))
# -----------------------------------------------------------------------------------------------------------

# -------------------------------------------- user input ---------------------------------------------------
    def getUserIntegerInput(self) -> int | None:
        userInput = input(" >> ").strip()

        if not userInput.isdigit():
            print(" ERROR: Input must be a number!")
            return None

        return int(userInput)

    def getUserFloatInput(self) -> float | None:
        userInput = input(" >> ").strip()
        if not userInput:
            print(" ERROR: Input must not be empty!")
            return None
        try:
            return float(userInput)
        except ValueError:
            print(" ERROR: Input must be a valid number!")
            return None

    def getUserStringInput(self) -> str | None:
        userInput = input(" >> ").strip()
        if not userInput:
            print(" ERROR: Input must not be empty!")
            return None
        else:
            return userInput
# -----------------------------------------------------------------------------------------------------------

# --------------------------------------------- override ----------------------------------------------------
    def setOverride(self, value: float):
        value = max(0.0, min(1.0, value))
        self.override = value
        self.robot.set_override(value)

# -----------------------------------------------------------------------------------------------------------

# --------------------------------------------- functions ---------------------------------------------------
    def changeMode(self):
        print("========== MODE SELECTION ==========")
        print(" MOVE       please press 1")
        print(" GRIP       please press 2")
        print(" SAVEPOINT  please press 3")
        print(" SETTINGS   please press 4")
        print(" DISCONNECT please press 8")
        print("====================================")

        userInput = self.getUserIntegerInput()

        match userInput:
            case 1:
                self.commandMode = CommandMode.MOVE
            case 2:
                self.commandMode = CommandMode.GRIP
            case 3:
                self.commandMode = CommandMode.SAVEPOINT
            case 4:
                self.commandMode = CommandMode.SETTINGS
            case 8:
                print("Disconnecting..")
                self.robot.disconnect()
            case _:
                print(" ERROR: Only numbers from 1 to 4 are allowed!")
                self.commandMode = CommandMode.CHANGEMODE

    def move(self):
        print()
        print("============ MOVE MENU =============")
        print(" 1 - PTP Joint")
        print(" 2 - PTP Cartesian")
        print(" 3 - LIN")
        print(" 4 - CIRC")
        print(" 9 - Change Mode")
        print("====================================")

        userInput = self.getUserIntegerInput()

        match userInput:
            case 1:
                print(" PTP Joint selected")
                # TODO: self.ptpJoint()

            case 2:
                print(" PTP Cartesian selected")
                self.ptpCartesian()

            case 3:
                print(" LIN selected")
                self.lin()

            case 4:
                print(" CIRC selected")
                # TODO: self.circ()

            case 9:
                print(" Change Mode selected")
                self.changeMode()

            case _:
                print(" ERROR: Invalid selection!")

    def grip(self):
        print()
        print("\n=== Gripper Menu ===")
        print(" 1 Jaw Gripper - Open")
        print(" 2 Jaw Gripper - Close")
        print(" 3 Vacuum - ON")
        print(" 4 Vacuum - OFF")
        print(" 5 Gripper settings")
        print(" 9 - Change Mode")
        print("=====================")


        userInput = self.getUserIntegerInput()

        match userInput:
            case 1:
                print(" Opening jaw gripper ...")
                self.robot.jaw_open()
                print(" Jaw gripper opened")

            case 2:
                print(" Closing jaw gripper ...")
                self.robot.jaw_close()
                print(" Jaw gripper closed")

            case 3:
                print(" Turning vacuum ON...")
                self.robot.vacuum_on()
                print(" Vacuum ON")

            case 4:
                print(" Turning vacuum OFF...")
                self.robot.vacuum_off()
                print(" Vacuum OFF")
            case 5:
                print(" TODO: Gripper settings selected")

            case 9:
                print(" Change Mode selected")
                self.commandMode = CommandMode.CHANGEMODE

            case _:
                print(" ERROR: Invalid option!")


    def savePoint(self):
        print()
        print("========== SAVE POINT MENU ==========")
        print(" 1 - Touchup")
        print(" 2 - Manual safe point")
        print(" 9 - Change Mode")
        print("====================================")

        userInput = self.getUserIntegerInput()

        match userInput:
            case 1:
                print(" Touchup selected")
                self.touchUp()

            case 2:
                print(" Manual safe point selected")
                self.manualSavePoint()

            case 9:
                print(" Change Mode selected")
                self.changeMode()


            case _:
                print(" ERROR: Invalid selection!")

    def settings(self):
            print()
            print("========== SETTINGS MENU ==========")
            print(" 1 - Set Tool")
            print(" 2 - Set Base")
            print(" 3 - Set Velocity")
            print(" 4 - Set Acceleration")
            print(" 5 - Set Blending")
            print(" 9 - Change Mode")
            print("====================================")

            userInput = self.getUserIntegerInput()

            match userInput:
                case 1:
                    self.setTool()
                case 2:
                    self.setBase()
                case 3:
                    self.setVelocity()
                case 4:
                    self.setAcceleration()
                case 5:
                    self.setBlending()
                case 9:
                    print(" Change Mode selected")
                    self.changeMode()
                case _:
                    print(" ERROR: Invalid selection!")
# -----------------------------------------------------------------------------------------------------------

# ------------------------------------------- move subfunctions ---------------------------------------------
    def ptpJoint(self):
        print("tbd")

    def ptpCartesian(self):
        print()
        print("======= PTP CARTESIAN =======")
        print(" Enter a point name OR manual values:")
        print(" Format for manual input: x y z a b c")
        print(" Example: 100 200 300 0 90 180")

        userInput = self.getUserStringInput()

        if not userInput:
            print(" ERROR: Input must not be empty!")
            return

        tempPoint = None

        # -----------------------------
        # 1) Manual Input
        # -----------------------------
        parts = userInput.split()
        if len(parts) == 6:
            try:
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
                a = float(parts[3])
                b = float(parts[4])
                c = float(parts[5])

                tempPoint = Point6D(
                    name="manual_input",
                    x=x, y=y, z=z,
                    a=a, b=b, c=c)

                print(" Manual point accepted.")
            except ValueError:
                print(" ERROR: Manual input must contain only numeric values!")
                return

        # -----------------------------
        # 2) CSV-Point
        # -----------------------------
        else:
            try:
                tempPoint : Point6D = load_point_csv(self.fileName, userInput)
                print(f" Point '{tempPoint.name}' loaded from CSV.")
            except KeyError as e:
                print(f" ERROR: {e}")
                return
            except Exception as e:
                print(f" ERROR while loading point: {e}")
                return

        # -----------------------------
        # 3) Velocity Input
        # -----------------------------
        print(" Enter velocity (0.1 - 10.0):")
        userInput = self.getUserStringInput()
        try:
            vel = float(userInput)
            if not 0.1 <= vel <= 10.0:
                raise ValueError
        except ValueError:
            print(f" ERROR: Invalid velocity! Using global velocity '{self.velocity}'")
            vel = self.velocity

        # -----------------------------

        print(" Sending PTP Cartesian move...")
        self.robot.ptp(
            point=tempPoint,
            vel=vel,
            base=self.base,
            tool=self.tool,
            blending=self.blending
        )

    def lin(self):
        print()
        print("============ LIN ============")
        print(" Enter a point name OR manual values:")
        print(" Format for manual input: x y z a b c")
        print(" Example: 100 200 300 0 90 180")

        userInput = self.getUserStringInput()

        if not userInput:
            print(" ERROR: Input must not be empty!")
            return

        tempPoint = None

        # -----------------------------
        # 1) Manual Input
        # -----------------------------
        parts = userInput.split()
        if len(parts) == 6:
            try:
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
                a = float(parts[3])
                b = float(parts[4])
                c = float(parts[5])

                tempPoint = Point6D(
                    name="manual_input",
                    x=x, y=y, z=z,
                    a=a, b=b, c=c)

                print(" Manual point accepted.")
            except ValueError:
                print(" ERROR: Manual input must contain only numeric values!")
                return

        # -----------------------------
        # 2) CSV-Point
        # -----------------------------
        else:
            try:
                tempPoint : Point6D = load_point_csv(self.fileName, userInput)
                print(f" Point '{tempPoint.name}' loaded from CSV.")
            except KeyError as e:
                print(f" ERROR: {e}")
                return
            except Exception as e:
                print(f" ERROR while loading point: {e}")
                return

        # -----------------------------
        # 3) Velocity Input
        # -----------------------------
        print(" Enter velocity (0.1 - 10.0):")
        userInput = self.getUserStringInput()
        try:
            vel = float(userInput)
            if not 0.1 <= vel <= 10.0:
                raise ValueError
        except ValueError:
            print(f" ERROR: Invalid velocity! Using global velocity '{self.velocity}'")
            vel = self.velocity

        # -----------------------------

        print(" Sending LIN move...")
        self.robot.lin(
            point=tempPoint,
            vel=vel,
            base=self.base,
            tool=self.tool,
            blending=self.blending
        )

    def circ(self):
        print("tbd")
# -----------------------------------------------------------------------------------------------------------

# ------------------------------------------- savePoint subfunctions ----------------------------------------
    def touchUp(self):
        print()
        print("========== TOUCHUP ==========")
        print(" Enter name for the touchup point:")
        point_name = self.getUserStringInput()

        if not point_name:
            print(" ERROR: Point name must not be empty!")
            return

        try:
            point : Point6D = self.robot.touchup(point_name, self.fileName)
            print(f" Touchup point '{point.name}' successfully stored in {self.fileName}")
            print(f" Coordinates: X={point.x}, Y={point.y}, Z={point.z}, A={point.a}, B={point.b}, C={point.c}")
        except Exception as e:
            print(f" ERROR while storing touchup point: {e}")

    def manualSavePoint(self):
        print()
        print("========== MANUAL SAVE POINT ==========")
        print(" Enter name for the point: ")
        point_name = self.getUserStringInput()
        if not point_name:
            print(" ERROR: Point name must not be empty!")
            return

        print(" Enter coordinates x y z a b c (space separated): ")
        coords_input = self.getUserStringInput()
        parts = coords_input.strip().split()
        if len(parts) != 6:
            print(" ERROR: You must enter exactly 6 numeric values!")
            return

        try:
            x, y, z, a, b, c = map(float, parts)
        except ValueError:
            print(" ERROR: All coordinates must be valid numbers!")
            return

        point = Point6D(
            name=point_name,
            x=x, y=y, z=z,
            a=a, b=b, c=c
        )

        try:
            save_point_csv(self.fileName, point, overwrite=True)
            print(f" Point '{point.name}' successfully saved in {self.fileName}")
            print(f" Coordinates: x={x}, y={y}, z={z}, a={a}, b={b}, c={c}")
        except Exception as e:
            print(f" ERROR saving point: {e}")

# -----------------------------------------------------------------------------------------------------------

# ------------------------------------------- settings subfunctions -----------------------------------------
    def setTool(self):
        val = self.getUserIntegerInput()
        if val is not None:
            self.tool = val
            print(f" Tool set to {self.tool}")

    def setBase(self):
        val = self.getUserIntegerInput()
        if val is not None:
            self.base = val
            print(f" Base set to {self.base}")

    def setVelocity(self):
        val = self.getUserFloatInput()
        if val is not None:
            self.velocity = max(0.1, min(val, 10.0))
            print(f" Velocity set to {self.velocity}")

    def setAcceleration(self):
        val = self.getUserFloatInput()
        if val is not None:
            self.acceleration = val
            print(f" Acceleration set to {self.acceleration}")

    def setBlending(self):
        val = self.getUserFloatInput()
        if val is not None:
            self.blending = val
            print(f" Blending set to {self.blending}")
# -----------------------------------------------------------------------------------------------------------    # ---------------------- Gripper Commands ----------------------
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
            velocity: Gripper speed (0-100%)
            force: Grip force
            tolerance: Position tolerance
            base_position: Base position
            work_position: Work position
            teach_position: Teach position
            shift_position: Shift position
        """
        self.gripper_controller.jaw_open(
            velocity=velocity,
            force=force,
            tolerance=tolerance,
            base_position=base_position,
            work_position=work_position,
            teach_position=teach_position,
            shift_position=shift_position
        )
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
                velocity: Gripper speed (0-100%)
                force: Grip force
                tolerance: Position tolerance
                base_position: Base position
                work_position: Work position
                teach_position: Teach position
                shift_position: Shift position
            """
            self.gripper_controller.jaw_close(
                velocity=velocity,
                force=force,
                tolerance=tolerance,
                base_position=base_position,
                work_position=work_position,
                teach_position=teach_position,
                shift_position=shift_position
            )
            def vacuum_on(self, cylinder: float = 0.0) -> None:
                """Turn vacuum gripper ON."""
                self.gripper_controller.vacuum_on(cylinder=cylinder)

            def vacuum_off(self, cylinder: float = 0.0) -> None:
                """Turn vacuum gripper OFF."""
                self.gripper_controller.vacuum_off(cylinder=cylinder)