### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import numpy as np
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        voxel_house = np.zeros((6,5,3), dtype=np.uint8)
        #voxel_house[:,:,0] = 1#floor
        voxel_house[:,:,-1] = 1#ceil
        voxel_house[0,:,:] = 1#left
        voxel_house[-1,:,:] = 1#right
        voxel_house[:,0,:] = 1#front
        voxel_house[:,-1,:] = 1#back
        voxel_house[2,-1,0:2] = 0#door
        voxel_house[4,-1,1] = 0#window
        self.target_struct = voxel_house
        self.player_voxels:List[tuple[int,int,int]] = []

    def eval_player_house(self) -> float:
        idx = np.asarray(self.player_voxels, dtype=np.int32)
        if idx.size == 0:
            return 0.0
        idx -= idx.min(0)
        #make rotation invariant
        #TODO make flip / mirror invariant
        sim = 0.0
        for i in range(3):
            target = np.rot90(self.target_struct,i)
            player = np.zeros_like(target, dtype=np.uint8) 
            try:
                player[idx[:,0],idx[:,1],idx[:,2]] = 1
            except IndexError:
                continue # out of bounds, try next
            num_correct = player == target
            all_correct = num_correct.sum() / float(target.size)
            blocks_correct = (num_correct*target).sum() / float(target.sum())
            sim = max(sim, min(all_correct,blocks_correct))
            
        return sim
        
        
data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MuseumHall)
editor.spawn_entity(SpawnableEntities.VoxelBuilder, "stacker", location=(0, 0, 0))
editor.spawn_entity(SpawnableEntities.DataExchange, "database", location=(0, 11, 0))
editor.set_map_bounds(extends=(16,16,20))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def house_goal(goal_name: str):
    editor.set_goal_progress(goal_name, data.eval_player_house())

editor.set_goals_intro_text("We are building a tiny house for this exhibition! Look in the DataExchange for the building plan. You must lay bricks accordingly, but can choose colors as you see fit.")
editor.specify_goal("stack_goal", "Use the VoxelBuilder to build a tiny house.", house_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How does voxelbuilder / block stacker work?","How can I spawn bricks?"], """Use the VoxelBuilder and its 'build_voxel' functionl. Here is an example: 
[#9CDCFE](stacker) = [#4ABCA5](VoxelBuilder).[#DCDCAA](first)\(\)
[#9CDCFE](stacker).[#DCDCAA](build_voxel)\([#9CDCFE](location)=\([#B5CEA8](0),[#B5CEA8](0),[#B5CEA8](0)\),
                    [#9CDCFE](color) = [#4ABCA5](Colors).[#B5CEA8](Red),
                    [#9CDCFE](simulate_physics)=[#C586C0](False)\)""")

editor.add_hint(2,["What format is the building plan in?","Is the building plan some kind of voxel data format?", "How is the array in the data exchange structured?"], """The building plan is stored an 3d voxel array of shape (6,5,3). When you load it from the DataExchange it is recommended to convert it to a numpy array for easier processing. Each entry in the array tells you, if a brick is required at the specified position (1) or not (0).""")

editor.add_hint(4,["Where should I build the house?","Is the location of the house important?", "Is the rotation of the house important?"], """You start building the house where ever you want. Also feel free to build the house rotated by 90, 180 or 270 degrees.""")

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    pass
    


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    db = DataExchange.first()
    db.set_data("VoxelTarget", data.target_struct.tolist(), True)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type == "VoxelBuilder" and command == "BuildVoxel":
        loc_dict = val.get_json_dict()["Location"]
        loc = (int(loc_dict["x"]),int(loc_dict["y"]),int(loc_dict["z"]))
        data.player_voxels.append(loc)

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
