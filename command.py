# import keyboard
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
        # keyboard.add_hotkey("F9", lambda: self.robot.emergency_stop())
        # keyboard.add_hotkey("F10", lambda: self.robot.reset_abort())
        # keyboard.add_hotkey("+", lambda: self.robot.set_override(self.override + 0.1))
        # nkeyboard.add_hotkey("-", lambda: self.robot.set_override(self.override - 0.1))
        print("tbd - install keyboard")
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

# --------------------------------------------- functions ---------------------------------------------------
    def changeMode(self):
        print("========== MODE SELECTION ==========")
        print(" For MOVE       please press 1")
        print(" For GRIP       please press 2")
        print(" For SAVEPOINT  please press 3")
        print(" For SETTINGS   please press 4")
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
        print("...")

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
# -----------------------------------------------------------------------------------------------------------