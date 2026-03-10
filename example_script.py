"""
Example script: KUKA Robot Scripting
=====================================
This script demonstrates how to control the KUKA robot
programmatically — no interactive menus needed.

Just edit the commands below and run:
    python example_script.py
"""

from kuka_api import KukaRobot, Point6D
from time import sleep

# ── Connection (einmal verbinden, bleibt offen) ──────────────────────
robot = KukaRobot("10.181.116.51")
robot.connect()

# ── Global settings (apply to all subsequent moves) ──────────────────
robot.set_velocity(0.1)
robot.set_tool(15)
robot.set_base(0)

robot.gripper_close()
robot.move_sequence_from_csv("sequence_points.csv", mode="ptp", vel=0.1)
robot.gripper_open()


print("Script finished!")

# ── Verbindung offen halten (blockiert bis Ctrl+C) ───────────────────
# robot.keep_alive()

while robot.cmd_counter > robot.last_finished_id + 1:
    print(robot.last_finished_id, robot.cmd_counter)
    sleep(0.5)
    
# ── Disconnect nur wenn gewünscht ────────────────────────────────────
robot.disconnect()
