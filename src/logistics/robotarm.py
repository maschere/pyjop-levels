### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.delivered:int = 0
        

data = DataModel()


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.set_template_code(from_comment="### robot arm template code")
editor.select_map(SpawnableMaps.SmallWarehouse)
editor.spawn_entity(SpawnableEntities.TriggerZone, "DropOffTrigger", location=(-3.8, 2.0, 1.0), scale = (2.0, 8.0, 2.0))
editor.spawn_static_mesh(SpawnableMeshes.Dumpster, location = (-3.74, 6.273, 0.0), rotation=(0,0,90))

editor.spawn_entity(SpawnableEntities.RobotArm, "arm", location=(0, 0, 0.34))
editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColorWorldAligned, color=Colors.Slategray, location=(0, 0,-0.15))

def spawn():
    editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "DeliverMe", location=(1.5, 0.5,0), scale=(1,1,1.2), simulate_physics=True, is_temp=True)

def on_drop_off(handler:TriggerZone,gt:float,e:TriggerEvent):
    if e.entity_name == "DeliverMe":
        data.delivered += 1
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def drop_goal(goal_name: str):
    editor.set_goal_state(
        goal_name,
        GoalState.Success if data.delivered > 0 else GoalState.Open
    )
editor.specify_goal("dropGoal", "Pick up the barrel and drop it off in the big dumpster. You can solve this level with code or manually by hand.", drop_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. ###
def select_arm(gt:float, num:int, num_revealed:int):
    RobotArm.first().focus()
editor.add_hint(0,["How can I solve this level without code?"], "Simply select the RobotArm and give it commands manually. Here you'll need the setGrabberLocation and pickup/release functions. It's a little trial and error to get the correct positions, but when you zoom close to the selected robot arm you'll see a coordinate system that should help you out.", on_reveal=select_arm)

editor.add_hint(2,["How can I program a solution to solve this level?"], "It's a little bit of trial and error to get the correct positions you'll need to set. Zoom close to the selected robot arm  and you'll see a coordinate system that should help you out. Then look into the template code how to use set_grabber_location and then use pickp() / release() to pickup or drop-off the barrel.", on_reveal=select_arm)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    TriggerZone.first().on_triggered(on_drop_off)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    spawn()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### robot arm template code
arm = RobotArm.first()
#set grabber location to x (forward) 0.2m; y (right) -1m (so actually 1 meter to the left); z (up) 1.5m
arm.set_grabber_location([0.2,-1,1.5])