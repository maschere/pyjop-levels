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
        self.waypoints:set[str] = set()
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.ParkingLot)
editor.set_map_bounds(center = (0,0,0), extends=(100,100,16))
editor.spawn_entity(SpawnableEntities.SmartTracker,"gps", location = (1, 40, 2))
editor.spawn_entity(SpawnableEntities.RaceCar, "car", location=(0, 40, 0.5))

editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(0, -40, 0), scale = (80,0.4,0.02), material=SpawnableMaterials.SimpleEmissive, color = Colors.White)
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(0, 40, 0), scale = (80,0.4,0.02), material=SpawnableMaterials.SimpleEmissive, color = Colors.White)
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(-40, 0, 0), scale = (0.4,80,0.02), material=SpawnableMaterials.SimpleEmissive, color = Colors.White)
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(40, 0, 0), scale = (0.4,80,0.02), material=SpawnableMaterials.SimpleEmissive, color = Colors.White)


editor.spawn_entity(SpawnableEntities.SmartSpotLight, "waypoint1", location=(40, 40, 3), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trigger_point1", location=(40, 40, 1), scale = 3)
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "waypoint2", location=(40, -40, 3), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trigger_point2", location=(40, -40, 1), scale = 3)
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "waypoint3", location=(-40, -40, 3), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trigger_point3", location=(-40, -40, 1), scale = 3)
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "waypoint4", location=(-40, 40, 3), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trigger_point4", location=(-40, 40, 1), scale = 3)

#need car / drone / etc to drive at random speeds
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

    
    

def speedo_goal(goal_name: str):
    if data.crossed_finish_at > 0:
        editor.set_goal_state(goal_name,GoalState.Success)
    else:
        editor.set_goal_state(goal_name,GoalState.Open)
        editor.set_goal_progress(goal_name, len(data.waypoints) / 4)

def time_goal(goal_name: str):
    TIME_LIMIT = 60.0
    if editor.get_goal_state(goal_name) == GoalState.Success:
        return
    t = max(0,TIME_LIMIT-SimEnvManager.first().get_sim_time())
    msg = f"Finish in under 60 seconds. Time Remaining: {t:.2f}"
    if data.crossed_finish_at > TIME_LIMIT:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    elif data.crossed_finish_at > 0:
        editor.set_goal_state(goal_name,GoalState.Success, msg)
    elif t <= 0:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    else:
        editor.set_goal_state(goal_name,GoalState.Open, msg)
editor.specify_goal("speedo", "Race along this 320m rectangular track. A GPS can help you guide the car towards the four corner waypoints at \(40,40\), \(40,-40\), \(-40,-40\), \(-40,40\) respectively.", speedo_goal)
editor.specify_goal("time_goal", "Finish in under 60 seconds.", time_goal, 0, True, True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
editor.add_hint(0,["The car won't move!","I set the throttle but the car is not driving.","How do I drive backwards?"], "Setting the throttle just means putting your foot on the gas pedal. You still need to shift into a gear to move forwards or backwards.")
editor.add_hint(2,["Where is the finish line?"], "There is none. You just have to drive through all 4 waypoints.")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###

def on_waypoint(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name == "car" and data.crossed_finish_at <= 0 and trigger.entity_name not in data.waypoints:
        data.waypoints.add(trigger.entity_name)
        waypoint_name = f"waypoint{trigger.entity_name[-1]}"
        SmartLight.find(waypoint_name).set_color(Colors.Green)
        if len(data.waypoints) >= 4:
            data.crossed_finish_at = dat.at_time
            editor.show_vfx(SpawnableVFX.Fireworks1, location = editor.get_location("car") - [0,0,5])

def begin_play():
    print("begin play")
    for t in TriggerZone.find_all():
        t.on_triggered(on_waypoint)
    
    on_reset()
    RaceCar.first().focus()
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint([0.5,0,10],[0,-89,0],1),
    #     CameraWaypoint([-2.5,0,4],[0,-70,0],2),
    #     CameraWaypoint([-7,0,2.5],[0,-15,0],2),
    #     CameraWaypoint([-7.1,0,2.3],[0,-14,0],3),
    #     CameraWaypoint([-7.2,0,2],[0,-13,0],1)
    # ])
    
    


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    editor.set_location("gps", (1, 40, 2))
    editor.weld_entities("gps","car")
    data.reset()
    for light in SmartLight.find_all():
        if "waypoint" in light.entity_name:
            light.set_color(Colors.Red)
            light.set_intensity(50)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
