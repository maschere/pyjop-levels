### INIT CODE - DO NOT CHANGE ###
from pyjop import *
from types import SimpleNamespace

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
        self.crossed_finish = False

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MinimalisticIndoor)
editor.spawn_entity(SpawnableEntities.HumanoidRobot, "runner", location=(0, 0, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "finish", location=(100, 0, 0), scale = (1,5,2))
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "finishlight", location=(100, 0, 3), rotation = (0,10,0))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def speedo_goal(goal_name: str):
    if data.crossed_finish:
        editor.set_goal_state(goal_name,GoalState.Success)
    else:
        editor.set_goal_state(goal_name,GoalState.Open)

editor.specify_goal("speedo_goal", "Run a 100m track as fast as you can.", speedo_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_finish_line(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name == "runner" and not data.crossed_finish:
        data.crossed_finish = True
        light = SmartLight.find("finishlight")
        light.set_color(Colors.Green)
        editor.show_vfx(SpawnableVFX.Fireworks1, location = (120, 0, -5))
        
def begin_play():
    print("begin play")
    t = TriggerZone.first()
    t.on_triggered(on_finish_line)
    SmartLight.find("finishlight").set_color(Colors.Red)
    SmartLight.find("finishlight").set_intensity(50)


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
