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
        self.vals = [round(random.uniform(1,5),3) for i in range(8)]
        self.sorted_idx = sorted(range(len(self.vals)), key=self.vals.__getitem__)
        self.command_count = 0
        
        
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanA",location = (0,-3,0.2), rotation = (0,0,180))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"posA",location = (0,-3,0.2))
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanB",location = (0,3,0.2), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"posB",location = (0,3,0.2))
editor.spawn_entity(SpawnableEntities.PushButton,"swap",location = (-3,0,0.25), scale = 3)

def spawn_blocks():
    #spawn 10 deliverables with random values
    data.reset()
    for i,v in enumerate(data.vals):
        editor.spawn_static_mesh(SpawnableMeshes.Cube, f"box_{i}", location = (i,0,0.5), scale = (.5,.5,v), material = SpawnableMaterials.SimpleColor, color = ((v-1)/4,.2,.2), is_temp=True)
    
        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def sort_goal(goal_name:str):
    prog = 0.0
    user_vals = []
    for i in range(len(data.vals)):
        user_vals.append(editor.get_location(f"box_{i}").x)
    
    user_sort = sorted(range(len(user_vals)), key=user_vals.__getitem__)
    for i,e in enumerate(user_sort):
        if e == data.sorted_idx[i]:
            prog += 1.0
    if data.command_count <= 0:
        prog = 0.001
    editor.set_goal_progress(goal_name, prog/len(data.vals))
    


CMD_LIMIT = 8
def cmd_goal(goal_name: str):
    s = GoalState.Success
    if data.command_count <= 0:
        s = GoalState.Open
    elif data.command_count > CMD_LIMIT:
        s = GoalState.Fail
    editor.set_goal_state(
        goal_name,
        s,
        f"Make at most {CMD_LIMIT} swaps. Current swap count: {data.command_count}/{CMD_LIMIT}"
    )
editor.specify_goal("cmdGoal", f"Make at most {CMD_LIMIT} swaps. Current swap count: {data.command_count}/{CMD_LIMIT}", cmd_goal,0,True,True)
editor.specify_goal("SortGoal","Sort all blocks from highest to lowest. \(The lowest block should be next to the button.\)", sort_goal)
editor.set_goals_intro_text("You can swap the position of the two boxes hit by the lasers of the two RangeFinders by pressing the PushButton.")
### END GOAL CODE ###


def on_swap(sender,simtime):
    scanA = RangeFinder.find("scanA")
    scanB = RangeFinder.find("scanB")
    boxA = scanA.get_entity_name()
    boxB = scanB.get_entity_name()
    if boxA and boxB and boxA!=boxB:
        data.command_count += 1
        loc_a = editor.get_location(boxA)
        loc_b = editor.get_location(boxB)
        editor.set_location(boxA,loc_b)
        editor.set_location(boxB,loc_a)
        
    

### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
    PushButton.first().on_press(on_swap)
    editor.ping(target_entity="swap")
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    platforms = MovablePlatform.find_all()
    for platform in platforms:
        platform.editor_set_rotation_limits([0,0,180])
        platform.editor_set_location_limits([9,0,0])
        platform.attach_entities()
    for rf in RangeFinder.find_all():
        rf.editor_set_can_read_physics(True)
        rf.editor_set_can_read_entities(True)
    spawn_blocks()
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###
editor.add_hint(2,["get_size does not return the height of the boxes, but rather three values. Which one is the height?"], "The last one at index 2. get_size actually returns the axis aligned bounding box (AABB) of the scanned object in x,y,z orientation in meters.")

editor.add_hint(4,["How do I swap boxes?", "Pressing swap does not work!"], "To swap the position of two blocks point scanA to one block and scanB to another. Then press the swap button.")
### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
