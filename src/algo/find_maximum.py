### INIT CODE - DO NOT CHANGE ###
from pyjop import *
import types
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.max_val:float = -1.2
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanner",location = (0,-3,0.2), rotation = (0,0,180))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"platform",location = (0,-3,0.2))
editor.spawn_entity(SpawnableEntities.InputBox,"result",location = (0,-6,1))

def spawn_blocks():
    #spawn 10 deliverables with random values
    data.reset()
    for i in range(10):
        val = round(0.25 + random.random()*4,2)
        data.max_val = max(val, data.max_val)
        editor.spawn_static_mesh(SpawnableMeshes.Cube, location = (i,0,0.5), scale = (.5,.5,0.75+val), material = SpawnableMaterials.SimpleColor, color = ((val-0.25)/5,.2,.2), is_temp=True)
    data.max_val += 0.75

        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def max_goal(goal_name:str):
    user_max = -5.7686
    user_raw = ""
    try:
        user_raw = InputBox.first().get_text()
        user_max = float(user_raw.replace(",","."))
    except:
        user_raw = ""
        pass
    editor.set_goal_state(goal_name, GoalState.Success if abs(user_max-data.max_val) < 0.001 else GoalState.Open if user_raw=="" else GoalState.Fail)
editor.specify_goal("MaxGoal","How high is the largest box? Enter the result into the InputBox \(programmatically or manually\).", max_goal)
### END GOAL CODE ###



### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    platform = MovablePlatform.first()
    platform.editor_set_rotation_limits([0,0,180])
    platform.editor_set_location_limits([9,0,0])
    platform.attach_entities()
    RangeFinder.first().editor_set_can_read_physics(True)
    spawn_blocks()
    InputBox.first().set_text("")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###
def select_box(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, """Please enter the maximum value here, e.g.: 1.4  ... You can do so manually or programmatically with the following snippet:
[#4ABCA5](InputBox).[#DCDCAA](first)\(\).[#DCDCAA](set_text)\([#CE9178]("1.4")\)
""")
    InputBox.first().focus()
editor.add_hint(0,["Where do I need to enter the maximum value once I found it?"], on_reveal=select_box)

editor.add_hint(2,["get_size does not return the height of the boxes, but rather three values. Which one is the height?"], "The last one at index 2. get_size actually returns the axis aligned bounding box (AABB) of the scanned object in x,y,z orientation in meters.")

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
