### INIT CODE - DO NOT CHANGE ###
from pyjop import *
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
import numpy as np
### END IMPORTS ###
SIZE = 20
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        
        mat = np.zeros((SIZE,SIZE), dtype=np.uint8)
        j = random.randint(6,8)
        for i in range(SIZE):
            mat[i,j] = 1
            j = clamp(j+random.choice([-1,1]),5,SIZE-6)
            mat[i,j] = 1
        i = random.randint(6,8)
        for j in range(SIZE):
            mat[i,j] = 1
            i = clamp(i+random.choice([-1,1]),5,SIZE-6)
            mat[i,j] = 1
        
        self.mat = np.pad(mat, 1, constant_values=1)
        self.player_voxels:Set[tuple[int,int]] = set()
        reg_mat = np.copy(self.mat)
        for regid in [2,3,4,5]:
            reg = []
            for i in range(reg_mat.shape[0]):
                for j in range(self.mat.shape[1]):
                    if reg_mat[i,j] == 0:
                        reg.append((i,j))
                        break
                if reg:
                    break
            #found start i,j
            while reg:
                i,j = reg.pop()
                reg_mat[i,j] = regid
                for a in [-1,0,1]:
                    for b in [-1,0,1]:
                        if reg_mat[i+a,j+b] == 0:
                            reg.append((i+a,j+b))
                            
        self.reg_mat = reg_mat
        self.target_reg = 0
        while True:
            i = random.randint(1,reg_mat.shape[0]-2)
            j = random.randint(1,reg_mat.shape[1]-2)
            if reg_mat[i,j] in [2,3,4,5]:
                self.mat[i,j] = 2
                self.target_reg = reg_mat[i,j]
                #print((i,j))
                break


    def eval_player(self) -> float:
        idx = np.asarray(list(self.player_voxels), dtype=np.int32)
        if idx.size == 0:
            return 0.0
        
        num_correct = 0.0
        try:
            if (self.reg_mat[idx[:,0],idx[:,1]] != self.target_reg).any():
                return -1.0
            num_correct = (self.reg_mat[idx[:,0],idx[:,1]] == self.target_reg).sum() / (self.reg_mat == self.target_reg).sum()
        except Exception:
            return -1.0

        return num_correct

        
                
                
        

    def spawn(self):
        for i in range(self.mat.shape[0]):
            for j in range(self.mat.shape[1]):
                if self.mat[i,j] == 1:
                    editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(i,j, 0.5), scale = 1, material=SpawnableMaterials.SimpleColor, color = 0.03, is_temp=True)
                if self.mat[i,j] > 1:
                    editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(i,j, 0.5), scale = 0.8, material=SpawnableMaterials.SimpleEmissive, color=(0.1,0,0), is_temp=True)
        #((v + random.randint(-20,20))%230,(v + random.randint(-20,20))%255,(v + random.randint(-20,20))%200)

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(center = (0,0,0), extends=(50,50,16))

#editor.spawn_entity(SpawnableEntities.ProximitySensor,"rfidSensor",location = (0,0,0))
editor.spawn_entity(SpawnableEntities.DataExchange,"database",location = (-2,0,0))
editor.spawn_entity(SpawnableEntities.VoxelBuilder, "stacker", location=(0, 0, 1))
        
### END CONSTRUCTION CODE ###

### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def fill_goal(goal_name: str):
    p = data.eval_player()
    if p < 0:
        editor.set_goal_state(goal_name, GoalState.Fail, "Do not place any Voxels outside the designated area! Please reset...")
    if p >= 0:
        editor.set_goal_progress(goal_name, p)

editor.set_goals_intro_text("Use the VoxelBuilder to to fill the designated region with red voxels. The 'VoxelTarget' in the DataExchange represents what you see here. It is a 22x22 matrix, where 0 indicates empty space, 1 a black wall and 2 is the starting location for the red voxels.")
editor.specify_goal("fill_goal", "Place all required voxels. Careful not to place any voxels outside the designated area.", fill_goal)
### END GOAL CODE ###



### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
    editor.ping(target_entity="stacker")
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    data.reset()
    data.spawn()
    db = DataExchange.first()
    db.set_data("VoxelTarget", data.mat.tolist())
    editor.set_goal_state("fill_goal",GoalState.Open,"Place all required voxels. Careful not to place any voxels outside the designated area.")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###

### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type == "VoxelBuilder" and command == "BuildVoxel":
        d = val.get_json_dict()
        loc_dict = d["Location"]
        loc = (int(loc_dict["x"]),int(loc_dict["y"]))
        if int(loc_dict["z"]) == 0:
            data.player_voxels.add(loc)

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

editor.set_template_code(from_comment="### get the voxel data")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### get the voxel data
dat = DataExchange.first().get_data("VoxelTarget")
print(dat)