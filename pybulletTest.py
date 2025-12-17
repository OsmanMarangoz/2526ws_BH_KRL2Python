import pybullet as p
import pybullet_data
import math
import time

# ------------------ Setup ------------------
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

plane = p.loadURDF("plane.urdf")

urdf_path = r"/home/lukas/Dokumente/KRL2Python/kuka\kuka_kr3_support\urdf\kr3r540.urdf"
robot = p.loadURDF(urdf_path, useFixedBase=True)

# ------------------ Reale KUKA-Gelenkwinkel ------------------
real_joint_angles_deg = [0.0, -90.0, 0.0, 0.0, 0.0, 45.0]
real_joint_angles_rad = [math.radians(a) for a in real_joint_angles_deg]

# Roboter initial setzen
for j in range(6):
    p.resetJointState(robot, j, real_joint_angles_rad[j])

# ------------------ Slider-Grenzen (Grad) ------------------
joint_limits_deg = [
    (-185, 185),   # A1
    (-120, 120),   # A2
    (-140, 140),   # A3
    (-350, 350),   # A4
    (-120, 120),   # A5
    (-350, 350)    # A6
]

# ------------------ Slider erzeugen (Initialwert = reale Winkel) ------------------
slider_ids = []
for i, (lo, hi) in enumerate(joint_limits_deg):
    slider = p.addUserDebugParameter(
        f"A{i+1} (deg)",
        lo,
        hi,
        real_joint_angles_deg[i]  # <<< HIER der Trick
    )
    slider_ids.append(slider)

# ------------------ Simulationsloop ------------------
while True:
    p.stepSimulation()

    # Slider lesen (Grad)
    deg_values = [p.readUserDebugParameter(s) for s in slider_ids]

    # In Radiant umrechnen
    rad_values = [math.radians(d) for d in deg_values]

    # Roboter steuern
    p.setJointMotorControlArray(
        robot,
        list(range(6)),
        p.POSITION_CONTROL,
        targetPositions=rad_values
    )

    time.sleep(1/240)