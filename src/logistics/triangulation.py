### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import math
### END IMPORTS ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.delivered:int = 0
        self.command_count:int = 0
        

data = DataModel()

### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.SmallWarehouse)

editor.spawn_entity(SpawnableEntities.TriggerZone, "DropOffTrigger", location=(-8.8, -3.0, 1.0), scale = (2.0, 8.0, 2.0))
editor.spawn_static_mesh(SpawnableMeshes.Dumpster, location = (-8.74, 1.273, 0.0), rotation=(0,0,90))
editor.spawn_entity(SpawnableEntities.GPSWaypoint,"DropOff",location = (-8.8, -3, 2.5))

editor.spawn_entity(SpawnableEntities.GPSWaypoint,"Origin",location = (0, 0, 2.5))
editor.spawn_entity(SpawnableEntities.RangeFinder, "A", location=(0, 0, 0), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.RangeFinder, "B", location=(0.2, 0.07, -0.2), rotation = (0,0,90))
editor.spawn_entity(SpawnableEntities.RangeFinder, "C", location=(10, 0, 0), rotation=(0,0,180))
editor.spawn_entity(SpawnableEntities.MovablePlatform, "platform", location=(-5, -5, 0.3))
editor.spawn_entity(SpawnableEntities.RobotArm, "arm", location=(-5, -5.2, 0.31))
editor.spawn_entity(SpawnableEntities.GPSWaypoint,"StartOffset",location = (-5, -5, 2.5))

def spawn_triangle():
    editor.destroy("B")
    sleep(0.1)
    b = random.uniform(2,7)
    a = random.uniform(2,7)
    c = math.sqrt(a*a + b*b)
    alpha = math.degrees(math.asin(a/c))
    editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "DeliverMe", location=(b, a, 0), scale=(1,1,1.2), simulate_physics=True)
    editor.set_rotation("A",(0,0,alpha+90))
    editor.set_location("C",(b,0,0))

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
editor.specify_goal("dropGoal", "Pick up the barrel and drop it off in the big dumpster.", drop_goal)

def cmd_goal(goal_name: str):
    s = GoalState.Success
    if data.command_count <= 0:
        s = GoalState.Open
    elif data.command_count > 6:
        s = GoalState.Fail
    editor.set_goal_state(
        goal_name,
        s,
        f"Issue at most 6 commands. Current command count: {data.command_count}/6"
    )
editor.specify_goal("cmdGoal", "Issue at most 6 commands. Current command count: 0/6", cmd_goal,0,True,True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
# editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")
# def select_conveyor(gt:float, num:int, num_revealed:int):
#     editor.change_hint(num, "Here it is!")
#     ConveyorBelt.find("belt1").focus()
# editor.add_hint(1,["Where is the conveyor belt?"], on_reveal=select_conveyor)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    TriggerZone.first().on_triggered(on_drop_off)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    MovablePlatform.first().attach_entities()
    MovablePlatform.first().editor_set_location_limits([20,20,5])
    MovablePlatform.first().editor_set_block_collisions(False)
    #RobotArm.first().editor_set_block_collisions(False)
    spawn_triangle()
    data.delivered = 0
    data.command_count = 0


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type=="RobotArm" or entity_type=="MovablePlatform":
        data.command_count += 1

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    pass


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
