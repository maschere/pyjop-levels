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
        self.mid_idx = random.randint(12,16)
        self.len = self.mid_idx*2 + 1
        self.locs:List[Vector3] = []
        self.idxA = 0
        self.idxB = 0
        self.command_count = 0
        self.mid_tag = ""
        self.command_limit = (self.len-1) + (self.len-1)//2 + 2
        
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(0,(200,32,16))
offset = -15
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanA",location = (0+offset,-4,0.2), rotation = (0,0,180))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"posA",location = (0+offset,-4,0.2), is_controllable=False)
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanB",location = (0+offset,4,0.2), rotation = (0,0,0))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"posB",location = (0+offset,4,0.2), is_controllable=False)
editor.spawn_entity(SpawnableEntities.PushButton,"nextA",location = (-3+offset,-4,0.25), scale = 3)
editor.spawn_entity(SpawnableEntities.PushButton,"nextB",location = (-3+offset,4,0.25), scale = 3)

editor.spawn_entity(SpawnableEntities.InputBox,"result",location = (-4+offset,0,1))
def spawn_linked_list():
    #spawn 10 deliverables with random values
    data.reset()
    last_loc = None
    for i in range(data.len):
        loc = Vector3(2*i + random.uniform(0,1.3),random.uniform(-3,3),0.9)
        if i == 0:
            loc.x = 0
            loc.y = 0
        data.locs.append(loc)
        loc = loc.copy()
        loc.x += offset
        tag = str(random.randint(1000,9999))
        editor.spawn_static_mesh(SpawnableMeshes.Sphere, location = loc, scale = 0.9, material = SpawnableMaterials.SimpleColor, color = Colors.Orange, is_temp=True, rfid_tag=tag)
        if i == data.mid_idx:
            data.mid_tag = tag
        if i > 0:
            angle = last_loc.find_lookat_rotation(loc).yaw
            mid = last_loc + (loc-last_loc)/2.0
            editor.spawn_static_mesh(SpawnableMeshes.Cube, location = mid, scale = ((loc-last_loc).length*1.1, 0.05, 0.05), rotation=(0,0,angle), material = SpawnableMaterials.SimpleEmissive, color = Vector3(0.1,0.12,0.8)*0.5, is_temp=True)
            editor.spawn_static_mesh(SpawnableMeshes.Cone, location = mid, scale = (0.5), rotation=(0,-90,angle), material = SpawnableMaterials.SimpleEmissive, color = Vector3(0.1,0.12,0.8) * 0.3, is_temp=True)
        last_loc = loc
    
        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def found_element():
    s = GoalState.Open
    user_val = ""
    try:
        user_val = InputBox.first().get_text()
    except:
        user_val = ""
        
    if len(user_val) >= 4:
        s = GoalState.Success if user_val == data.mid_tag else GoalState.Fail
    return s
def mid_goal(goal_name:str):
    editor.set_goal_state(goal_name, found_element())
    

def cmd_goal(goal_name: str):
    s = GoalState.Success
    if data.command_count <= 0:
        s = GoalState.Open
    elif data.command_count > data.command_limit:
        s = GoalState.Fail
    editor.set_goal_state(
        goal_name,
        s,
        f"Issue at most {data.command_limit} commands. Current command count: {data.command_count}/{data.command_limit}"
    )
TIME_LIMIT = 100.0
def time_goal(goal_name: str):
    
    if editor.get_goal_state(goal_name) == GoalState.Success:
        return
    t = max(0,TIME_LIMIT-SimEnvManager.first().get_sim_time())
    msg = f"Finish in under {int(TIME_LIMIT)} seconds. Time Remaining: {t:.2f}"

    if found_element() == GoalState.Success:
        if t > 0:
            editor.set_goal_state(goal_name,GoalState.Success, msg)
    elif t <= 0:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    else:
        editor.set_goal_state(goal_name,GoalState.Open, msg)
        
editor.specify_goal("time_goal", f"Finish in under {int(TIME_LIMIT)} seconds.", time_goal, 0, True, True)
editor.specify_goal("mid_goal","What is the RFID tag of the middle element in this linked list? Enter it in the InputBox.", mid_goal)
### END GOAL CODE ###


editor.add_hint(0,["How can I move the platform / the laser pointer?", "The MovablePlatform cannot be moved!"], """To simulate linked list behavior instead of random access behavior, you can only control the movable platform indirectly by pressing the PushButtons. For example, to move "scanA" to the next element in the list you'd call this code:
[#4ABCA5](PushButton).[#DCDCAA](find)\([#CE9178]("nextA")\).[#DCDCAA](press)\(\)
""")

def on_next(sender:PushButton,simtime):
    AorB = sender.entity_name[-1]
    platform = MovablePlatform.find("pos" + AorB)
    if AorB == "A":
        data.idxA +=1
        idx = data.idxA
    else:
        data.idxB +=1
        idx = data.idxB

    if idx < data.len:
        data.command_count += 1
        platform.set_target_location((data.locs[idx].x,0,0))
        
    

### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
    PushButton.find("nextA").on_press(on_next)
    PushButton.find("nextB").on_press(on_next)
    InputBox.first().set_text("")
    editor.set_goal_progress("mid_goal", 0.001)
    editor.ping(target_entity="nextA")
    editor.ping(target_entity="nextB")
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    platforms = MovablePlatform.find_all()
    for platform in platforms:
        platform.editor_set_rotation_limits([0,0,1])
        platform.editor_set_location_limits([100,0,0])
        platform.editor_set_movement_speed(50)
        platform.attach_entities()
        
    for rf in RangeFinder.find_all():
        rf.editor_set_can_read_rfid_tags(True)
    spawn_linked_list()
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
