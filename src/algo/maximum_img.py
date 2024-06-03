### INIT CODE - DO NOT CHANGE ###
from pyjop import *
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.max_idx:int = -1
        self.max_val:float = -1.5
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(center = (0,0,0), extends=(100,100,16))

editor.spawn_entity(SpawnableEntities.SmartCamera,"cam",location = (5,-35,1), rotation = (0,0,90), is_controllable=False)
editor.spawn_entity(SpawnableEntities.InputBox,"result",location = (-3,-7,1))


def spawn_blocks():
    #spawn 10 deliverables with random values
    data.reset()
    sizes = [x / 5.0 for x in range(0, 40,4)]
    sizes.sort(key=lambda x: random.random())
    for i in range(10):
        val = sizes[i]
        if val > data.max_val:
            data.max_val = val
            data.max_idx = i
        editor.spawn_static_mesh(SpawnableMeshes.Cube, location = (i,0,0.5), scale = (.5,.5,1+val), material = SpawnableMaterials.SimpleColor, color = (val/17,val/23,.2), is_temp=True)


        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def max_goal(goal_name:str):
    s = GoalState.Open
    user_max = -2
    user_raw = ""
    try:
        user_raw = InputBox.first().get_text()
        user_max = int(user_raw.replace(",","."))
    except:
        user_raw = ""
        pass
    if user_max >= 0:
        s = GoalState.Success if user_max == data.max_idx else GoalState.Fail
    editor.set_goal_state(goal_name, s)

editor.set_goals_intro_text("Find the largest box using the camera's image.")
editor.specify_goal("MaxGoal","What is the index of the largest box, starting from 0 at the rightmost box. Enter the result into the InputBox \(programmatically or manually\).", max_goal)
### END GOAL CODE ###



### ON BEGIN PLAY CODE ###
def begin_play():
    editor.ping(target_entity="cam")
    on_reset()
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    cam = SmartCamera.first()
    cam.editor_set_camera_type(CameraType.RGB)
    cam.set_fov(20)
    spawn_blocks()
    InputBox.first().set_text("")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###
editor.add_hint(0,["How do I obtain a camera frame?"], """[#9CDCFE](img) = [#9CDCFE](cam).[#DCDCAA](get_camera_frame)\(\)
[#DCDCAA](print)\([#9CDCFE](img).shape\)""")

def select_cam(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, "The camera is 35m in front of the blocks with a large zoom factor to minimize perspective distortion.")
    SmartCamera.first().focus()
editor.add_hint(2,["Where is the camera?", "Why is the camera so far back?"], on_reveal=select_cam)

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
