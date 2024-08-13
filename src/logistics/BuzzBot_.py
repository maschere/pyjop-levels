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
        self.sorted_count = 0
        
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.SmallWarehouse)
editor.spawn_entity(SpawnableEntities.ObjectSpawner, "spawner", location=(0, -0.4, 4))
editor.spawn_entity(SpawnableEntities.RobotArm, "robot_arm", location=(-2, 0, 0))
editor.spawn_static_mesh(SpawnableMeshes.Cube, "table")
editor.spawn_entity(SpawnableEntities.RangeFinder, "scanner", location=(0, 1, 0), rotation=(0, 0, 0))

editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, color=Colors.Blue, location=(-2, -2, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trig_blue", location=(-2, -2, 1))

editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, color=Colors.Red, location=(-2, 2, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trig_red", location=(-2, 2, 1))

editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, color=Colors.Yellow, location=(-4, 0, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "trig_yellow", location=(-4, 0, 1))

def spawn_temp_object():
    checksum = random.randint(111, 999)
    editor.spawn_static_mesh(SpawnableMeshes.CardboardBox, location=(0, 0, 3), rfid_tag=f"chk_sum={checksum}", is_temp=True, simulate_physics=True)

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Read the checksums of the boxes and move the box to blue if checksum is divisible by three, move to red if it's divisible by five, and move it to yellow if checksum is divisible by both three and five.")

def level_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        1 / 10,
        f"{data.sorted_count} boxes sorted correctly",
    )

editor.specify_goal("levelGoal", "Sort boxes", level_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    spawn_temp_object()
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    print(f"player command at {gametime}: {entity_type}.{entity_name}.{command}")

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    pass


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#this template code will be provided to the player
#add level specific hints or boilerplate code here.


env = SimEnvManager.first()

while SimEnv.run_main():
    pass