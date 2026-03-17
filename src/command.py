from unittest import case
import keyboard
import threading
from point import Point6D, JointState
from robot import Robot
from csvHelper import load_point_csv,save_point_csv,load_all_points_csv

from enum import Enum

class CommandMode(Enum):
    MOVE = 1
    GRIP = 2
    SAVEPOINT = 3
    SETTINGS = 4
    CHANGEMODE = 9

class Command:

    def __init__(self, robot):
        self.robot = robot
        self._safety_thread = None
        self._motion_thread = None

        self.commandMode = CommandMode.CHANGEMODE

        self.override = 100
        self.fileName = r"../database/points.csv"

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
        keyboard.add_hotkey("s", lambda: self.robot.abort())
        keyboard.add_hotkey("+", lambda: self.setOverride(self.override +10))
        keyboard.add_hotkey("-", lambda: self.setOverride(self.override -10))
# -----------------------------------------------------------------------------------------------------------
    def start_safety_thread(self):
        if self._safety_thread is not None and self._safety_thread.is_alive():
            return

        self._safety_thread = threading.Thread(
            target=self.safetyLoop,
            daemon=True
        )
        self._safety_thread.start()

    def start_motion_thread(self):
        if self._motion_thread is not None and self._motion_thread.is_alive():
            return

        self._motion_thread = threading.Thread(
            target=self.loop,
            daemon=True
        )
        self._motion_thread.start()
# -------------------------------------------- helper -------------------------------------------------------
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

    def getOptionalFloatInput(self, prompt: str = " >> ") -> float | None:
        userInput = input(prompt).strip()
        if userInput == "":
            return None
        try:
            return float(userInput)
        except ValueError:
            print(" ERROR: Input must be a valid number!")
            return None

    def getOptionalIntegerInput(self, prompt: str = " >> ") -> int | None:
        userInput = input(prompt).strip()
        if userInput == "":
            return None
        try:
            return int(userInput)
        except ValueError:
            print(" ERROR: Input must be a valid integer!")
            return None

    def readPointInput(self) -> Point6D | None:
        print(" Enter a point name OR manual values:")
        print(" Format for manual input: x y z a b c")

        userInput = self.getUserStringInput()
        if not userInput:
            return None

        parts = userInput.split()

        if len(parts) == 6:
            try:
                x, y, z, a, b, c = map(float, parts)
                return Point6D(
                    name="manual_input",
                    x=x, y=y, z=z,
                    a=a, b=b, c=c
                )
            except ValueError:
                print(" ERROR: Manual input must contain only numeric values!")
                return None

        try:
            point = load_point_csv(self.fileName, userInput)
            print(f" Point '{point.name}' loaded from CSV.")
            return point
        except Exception as e:
            print(f" ERROR while loading point: {e}")
            return None

    def readMotionOverrides(self):
        print(f" Velocity [{self.robot.default_velocity}] (Enter = default):")
        vel = self.getOptionalFloatInput()

        print(f" Acceleration [{self.robot.default_acceleration}] (Enter = default):")
        acc = self.getOptionalFloatInput()

        print(f" Blending [{self.robot.default_blending}] (Enter = default):")
        blending = self.getOptionalFloatInput()

        print(f" Base [{self.robot.default_base}] (Enter = default):")
        base = self.getOptionalIntegerInput()

        print(f" Tool [{self.robot.default_tool}] (Enter = default):")
        tool = self.getOptionalIntegerInput()

        return vel, acc, base, tool, blending
# -----------------------------------------------------------------------------------------------------------

# --------------------------------------------- override ----------------------------------------------------
    def setOverride(self, value: int):
        value = max(0, min(100, value))
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
        print(" 5 - Move in Sequence [PTP]")
        print(" 6 - Move in Sequence [LIN]")
        print(" 9 - Change Mode")
        print("====================================")

        userInput = self.getUserIntegerInput()

        match userInput:
            case 1:
                print(" PTP Joint selected")
                self.ptpJoint()

            case 2:
                print(" PTP Cartesian selected")
                self.ptpCartesian()

            case 3:
                print(" LIN selected")
                self.lin()

            case 4:
                print(" CIRC selected")
                self.circ()

            case 5:
                print(" Move in Sequence [PTP] selected")
                self.ptpCartesianSequence()

            case 6:
                print(" Move in Sequence [LIN] selected")
                self.linSequence()

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

            case 9:
                print(" Change Mode selected")
                self.changeMode()

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
        print()
        print("========== PTP JOINT ==========")
        print(" Enter joint values: a1 a2 a3 a4 a5 a6")
        print(" Example: 0 -90 90 0 45 0")

        userInput = self.getUserStringInput()
        if not userInput:
            return

        parts = userInput.split()
        if len(parts) != 6:
            print(" ERROR: Please enter exactly 6 joint values.")
            return

        try:
            a1, a2, a3, a4, a5, a6 = map(float, parts)
        except ValueError:
            print(" ERROR: Joint values must be numeric.")
            return

        joints = JointState(
            a1=a1,
            a2=a2,
            a3=a3,
            a4=a4,
            a5=a5,
            a6=a6
        )

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending PTP Joint move...")
        self.robot.ptp_joint(
            joints=joints,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def ptpCartesian(self):
        print()
        print("======= PTP CARTESIAN =======")

        point = self.readPointInput()
        if point is None:
            return

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending PTP Cartesian move...")
        self.robot.ptp(
            point=point,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def lin(self):
        print()
        print("============ LIN ============")

        point = self.readPointInput()
        if point is None:
            return

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending LIN move...")
        self.robot.lin(
            point=point,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def circ(self):
        print()
        print("============ CIRC ============")
        print(" Enter AUX point name OR manual values:")
        auxPoint = self.readPointInput()
        if auxPoint is None:
            return

        print(" Enter END point name OR manual values:")
        endPoint = self.readPointInput()
        if endPoint is None:
            return

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending CIRC move...")
        self.robot.circ(
            end=endPoint,
            aux=auxPoint,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )
# ------------------------------------------- move sequence subfunctions ------------------------------------
    def ptpCartesianSequence(self):
        print()
        print("======= PTP CARTESIAN SEQUENCE =======")
        print(" Choose CSV file:")

        available_csv = []
        try:
            from pathlib import Path
            csv_dir = Path(__file__).resolve().parent
            available_csv = sorted([p.name for p in csv_dir.glob("*.csv")])

            if available_csv:
                print(" Available CSV files:")
                for idx, name in enumerate(available_csv, start=1):
                    print(f"  {idx}. {name}")
            else:
                print(" No CSV files found in project folder; default=points.csv will be used.")
        except Exception as e:
            print(f" WARNING: Could not list CSV files automatically: {e}")

        print(f" Default: {self.fileName}")
        csv_choice = input(" >> ").strip()

        chosen_file = self.fileName
        if csv_choice:
            if csv_choice.isdigit() and available_csv:
                idx = int(csv_choice)
                if 1 <= idx <= len(available_csv):
                    chosen_file = available_csv[idx - 1]
                else:
                    print(" ERROR: Invalid selection number. Using default.")
            else:
                if not csv_choice.endswith(".csv"):
                    csv_choice += ".csv"
                chosen_file = csv_choice

        print(f" Loading & Sequencing all points from '{chosen_file}' ...")

        try:
            points = load_all_points_csv(chosen_file)
            if not points:
                print(" ERROR: No points found in CSV.")
                return
            print(f" Loaded {len(points)} points.")
        except Exception as e:
            print(f" ERROR while loading points: {e}")
            return

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending PTP Cartesian sequence...")
        self.robot.move_sequence(
            points=points,
            mode=2,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )

    def linSequence(self):
        print()
        print("======= LIN SEQUENCE =======")
        print(" Choose CSV file:")

        available_csv = []
        try:
            from pathlib import Path
            csv_dir = Path(__file__).resolve().parent
            available_csv = sorted([p.name for p in csv_dir.glob("*.csv")])

            if available_csv:
                print(" Available CSV files:")
                for idx, name in enumerate(available_csv, start=1):
                    print(f"  {idx}. {name}")
            else:
                print(" No CSV files found in project folder; default=points.csv will be used.")
        except Exception as e:
            print(f" WARNING: Could not list CSV files automatically: {e}")

        print(f" Default: {self.fileName}")
        csv_choice = input(" >> ").strip()

        chosen_file = self.fileName
        if csv_choice:
            if csv_choice.isdigit() and available_csv:
                idx = int(csv_choice)
                if 1 <= idx <= len(available_csv):
                    chosen_file = available_csv[idx - 1]
                else:
                    print(" ERROR: Invalid selection number. Using default.")
            else:
                if not csv_choice.endswith(".csv"):
                    csv_choice += ".csv"
                chosen_file = csv_choice

        print(f" Loading & Sequencing all points from '{chosen_file}' ...")

        try:
            points = load_all_points_csv(chosen_file)
            if not points:
                print(" ERROR: No points found in CSV.")
                return
            print(f" Loaded {len(points)} points.")
        except Exception as e:
            print(f" ERROR while loading points: {e}")
            return

        vel, acc, base, tool, blending = self.readMotionOverrides()

        print(" Sending PTP Cartesian sequence...")
        self.robot.move_sequence(
            points=points,
            mode=3,
            vel=vel,
            acc=acc,
            base=base,
            tool=tool,
            blending=blending
        )
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
        print(f" Tool [{self.robot.default_tool}]")
        val = self.getUserIntegerInput()
        if val is not None:
            self.robot.set_default_tool(val)
            print(f" Set to Tool [{self.robot.default_tool}]")

    def setBase(self):
        print(f" Base [{self.robot.default_base}]")
        val = self.getUserIntegerInput()
        if val is not None:
            self.robot.set_default_base(val)
            print(f" Set to Base [{self.robot.default_base}]")

    def setVelocity(self):
        print(f" Velocity [{self.robot.default_velocity}]")
        val = self.getUserFloatInput()
        if val is not None:
            self.robot.set_default_velocity(val)
            print(f" Set to Velocity [{self.robot.default_velocity}]")

    def setAcceleration(self):
        print(f" Acceleration [{self.robot.default_acceleration}]")
        val = self.getUserFloatInput()
        if val is not None:
            self.robot.set_default_acceleration(val)
            print(f" Set to Acceleration [{self.robot.default_acceleration}]")

    def setBlending(self):
        print(f" Blending [{self.robot.default_blending}]")
        val = self.getUserFloatInput()
        if val is not None:
            self.robot.set_default_blending(val)
            print(f" Set to Blending [{self.robot.default_blending}]")
# -----------------------------------------------------------------------------------------------------------