### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.crossed_finish_at = -1.0
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.ParkingLot)
editor.set_map_bounds(center = (250,0,0), extends=(520,10,16))
editor.spawn_entity(SpawnableEntities.RaceCar, "car", location=(0, 0, 0.5))
editor.spawn_entity(SpawnableEntities.TriggerZone, "finish", location=(500, 0, 0), scale = (2,10,2))
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(250, 0, 0), scale = (500,0.4,0.02), material=SpawnableMaterials.SimpleEmissive, color = Colors.White)
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "finishlight", location=(500, 0, 3), rotation = (0,10,0))

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

    
    

def speedo_goal(goal_name: str):
    if data.crossed_finish_at > 0:
        editor.set_goal_state(goal_name,GoalState.Success)
    else:
        editor.set_goal_state(goal_name,GoalState.Open)

def time_goal(goal_name: str):
    TIME_LIMIT = 15.0
    if editor.get_goal_state(goal_name) == GoalState.Success:
        return
    t = max(0,TIME_LIMIT-SimEnvManager.first().get_sim_time())
    msg = f"Finish in under 15 seconds. Time Remaining: {t:.2f}"
    if data.crossed_finish_at > TIME_LIMIT:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    elif data.crossed_finish_at > 0:
        editor.set_goal_state(goal_name,GoalState.Success, msg)
    elif t <= 0:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    else:
        editor.set_goal_state(goal_name,GoalState.Open, msg)
editor.specify_goal("speedo", "Race down this 500 meters long straight track as fast as possible.", speedo_goal)
editor.specify_goal("time_goal", "Finish in under 15 seconds.", time_goal, 0, True, True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. ###
editor.add_hint(0,["The car won't move!","I set the throttle but the car is not driving.","How do I drive backwards?"], "Setting the throttle just means putting your foot on the gas pedal. You still need to shift into a gear to move forwards or backwards.")
editor.add_hint(2,["Where is the finish line?"], "It's 500 meters straight down. Don't do any steering, just go forwards.")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###

def on_finish_line(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name == "car" and data.crossed_finish_at <= 0:
        data.crossed_finish_at = dat.at_time
        light = SmartLight.find("finishlight")
        light.set_color(Colors.Green)
        editor.show_vfx(SpawnableVFX.Fireworks1, location = (520, 0, -5))

def begin_play():
    print("begin play")
    t = TriggerZone.first()
    t.on_triggered(on_finish_line)
    SmartLight.find("finishlight").set_color(Colors.Red)
    SmartLight.find("finishlight").set_intensity(50)
    RaceCar.first().set_lights(True)
    on_reset()
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint([0.5,0,10],[0,-89,0],1),
    #     CameraWaypoint([-2.5,0,4],[0,-70,0],2),
    #     CameraWaypoint([-7,0,2.5],[0,-15,0],2),
    #     CameraWaypoint([-7.1,0,2.3],[0,-14,0],1),
    #     CameraWaypoint([100,0,2],[0,-13,0],2)
    # ])
    
    


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
