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
        self.z_levels:Set[int] = set()
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MuseumHall)
editor.spawn_entity(SpawnableEntities.VoxelBuilder, "stacker", location=(0, 0, 0))
editor.set_map_bounds(extends=(16,16,20))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def stack_goal(goal_name: str):

    levels = sorted(list(data.z_levels))
    height = 0
    for i,e in enumerate(levels):
        height = i+1
        if i == 0:
            continue
        if levels[i-1] != e-1:
            break
    
    editor.set_goal_progress(
        goal_name,
        height / 15
    )


editor.specify_goal("stack_goal", "Use the VoxelBuilder to stack a tower at least 15 bricks high. The rest is up to your creativity.", stack_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How does voxelbuilder / block stacker work?","How can I spawn bricks?"], """Use the VoxelBuilder and its 'build_voxel' functionl. Here is an example: 
[#9CDCFE](stacker) = [#4ABCA5](VoxelBuilder).[#DCDCAA](first)\(\)
[#9CDCFE](stacker).[#DCDCAA](build_voxel)\([#9CDCFE](location)=\([#B5CEA8](0),[#B5CEA8](0),[#B5CEA8](0)\),
                    [#9CDCFE](color) = [#4ABCA5](Colors).[#B5CEA8](Red),
                    [#9CDCFE](simulate_physics)=[#C586C0](False)\)""")

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type == "VoxelBuilder" and command == "BuildVoxel":
        loc_z = int(val.get_json_dict()["Location"]["z"])
        if loc_z >= 0 and loc_z <=20:
            data.z_levels.add(loc_z)

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###


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
