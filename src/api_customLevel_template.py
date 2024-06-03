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
        self.time_counter = 0.0
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MinimalisticIndoor)
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt1", location=(0, 0, 0))
def spawn_temp_object():
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it often makes sense to call this function on each level reset to respawn the temp objects in their original location.
    for i in range(3):
        editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(i-1, 0, 3), scale = 0.8, simulate_physics=True, is_temp = True, material=SpawnableMaterials.SimpleColor, color=Colors.Brown)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Welcome to the level editor.")

def sample_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        SimEnvManager.first().get_sim_time() / 30,
        f"Wait for {int(30)-SimEnvManager.first().get_sim_time()} seconds to complete this level.",
    )

editor.specify_goal("testGoal", "Wait for 30 seconds", sample_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")

def select_conveyor(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, "Here it is!")
    ConveyorBelt.find("belt1").focus()
editor.add_hint(3,["Where is the conveyor belt?"], on_reveal=select_conveyor)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    editor.show_video(SpawnableVideos.ManimPrintHello)
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
    if data.time_counter > 5:
        print("hello every 5 seconds")
        data.time_counter = 0.0
    else:
        data.time_counter += deltatime


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
print("hello world")

env = SimEnvManager.first()

while SimEnv.run_main():
    # main loop to retrieve data from the SimEnv, calculate stuff and send commands back into the SimEnv
    # for example, get current time and display it
    simtime = env.get_sim_time()
    print(f"current time: {simtime} seconds")
