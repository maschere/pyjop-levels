### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.parking_duration = 0.0
        self.ts = 1.0

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.ParkingLot)
editor.spawn_entity(
    SpawnableEntities.ServiceDrone, "drone", location=(0, random.random(), 0)
)
editor.spawn_entity(SpawnableEntities.RangeFinder, "range", location=(0, 10, 0.75))
editor.spawn_static_mesh(
    SpawnableMeshes.Cube,
    material=SpawnableMaterials.SimpleColor,
    location=(0, 10, 0),
    scale=(1, 1, 1.5),
    color=Colors.Slategray,
)
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def parking_goal(goal_name: str):
    rangefinder = RangeFinder.first()
    d = rangefinder.get_distance()
    m = SimEnvManager.first()
    ts2 = m.get_sim_time()
    dts = max(0, ts2 - data.ts)
    data.ts = ts2
    if 2.99 < d < 3.01:
        data.parking_duration += dts
    else:
        data.parking_duration = 0

    editor.set_goal_progress(
        goal_name,
        data.parking_duration / 5,
        f"Move the drone precisely 3m in front of the RangeFinder and stop there for at least 5 seconds. Distance: {d:.3f}m, Parking duration: {data.parking_duration:.2f}s",
    )

def time_limit(goal_name: str):
    ts = SimEnvManager.first().get_sim_time()
    time_remain = max(0.0, 15 - ts)

    s = GoalState.Unknown
    if data.parking_duration >= 4.8:
        if time_remain > 0: 
            s = GoalState.Success
    elif time_remain > 0:
        s = GoalState.Open
    else:
        s = GoalState.Fail

    if s == GoalState.Unknown:
        return
    editor.set_goal_state(
        goal_name,
        s,
        f"Park the drone within 15 seconds \\(Time remaining: {time_remain:.2f}\\)",
    )


editor.specify_goal(
    "parking",
    "Move the drone precisely 3m in front of the RangeFinder and stop there for at least 5 seconds.",
    parking_goal,
    1
)

editor.specify_goal(
    "timelimit", f"Park the drone within 15 seconds.", time_limit, 0, is_optional=True
)

### END GOAL CODE ###

### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
editor.add_hint(0,["The time limit seems impossible","How can I beat the time limit?", "15 seconds is not enough to beat this!", "How can I reset the level before my code starts?"], "Consider resetting the level from your python code just before your actual control code:\n[#4ABCA5](SimEnvManager).[#DCDCAA](first)\(\).[#DCDCAA,TooltipEmph](reset)\(\)")
editor.add_hint(1,["The drone overshoots or undershoots the target position!", "My simple IF clause is not controlling the drone properly."], "Consider looking into PID controllers. At the very least, use a proportional component: Scale the amount of thrust you apply to the drone with the remaining distance to the target position.")
editor.add_hint(2,["What is a PID controller?", "How does PID control work?", "Should I use a PID or other control theory in this simulation?"], "A basic PID controller should work well in this simulation. Actually the P component alone can do most of the heavy lifting. In general, a PID controller calculates some output signal \(thrust in this case\) based on the sum of scaled error (P), derivate or change in error (D) and sum of error over time (I).")
def showoff_dron(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, """Here is the drone and an example script I'm running now:
[#9CDCFE](drone) = [#4ABCA5](ServiceDrone).[#DCDCAA](first)\(\)
[#6A9955](#give short boost forwards)
[#9CDCFE](drone).[#DCDCAA](apply_thruster_impulse_left)\([#B5CEA8](200)\)
[#9CDCFE](drone).[#DCDCAA](apply_thruster_impulse_right)\([#B5CEA8](200)\)""")
    drone = ServiceDrone.first()
    drone.focus()
    sleep(1)
    drone.apply_thruster_impulse_left(200)
    drone.apply_thruster_impulse_right(200)
    
editor.add_hint(3,["How can I control the drone?","What am I supposed to do with the drone?", "Show what the drone can do!"], on_reveal=showoff_dron)

editor.add_hint(5,["How can I stop the drone at its current location?"], "Stopping the drone is not as easy as it might sound. For stars you set the thruster force to 0, but then the drone will still drift a little further. So you need to apply a short impuslse in the opposite direction (you can apply a negative impulse as well). This impulse should depend on the current speed of the drone.")

### END HINTS ###


### DYNAMIC LEVEL CODE ###
def begin_play():
    print("begin play")
    editor.set_enabled("drone", is_enabled=False, component_name="DistanceLeft")
    editor.set_enabled("drone", is_enabled=False, component_name="DistanceRight")
    editor.set_enabled("drone", is_enabled=False, component_name="Camera")


editor.on_begin_play(begin_play)
### END DYNAMIC LEVEL CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    editor.set_location("drone", (0, random.random(), 0))
    data.reset()

editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")

### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###

### PLAYER TEMPLATE CODE ###
# This level has an optional time limit challenge. To reset the timer, use the following command (this is the same command as pressing the "reset" button on the lower right-hand corner in the game's GUI)
env = SimEnvManager.first()
env.reset()

scanner = RangeFinder.first()

while SimEnv.run_main():
    # main loop to retrieve data from the SimEnv, calculate stuff and send commands back into the SimEnv
    dist = scanner.get_distance()
    print(f"current distance: {dist:.3f}m")
