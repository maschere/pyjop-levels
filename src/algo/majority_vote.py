### INIT CODE - DO NOT CHANGE ###
from pyjop import *
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
import numpy as np
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        vals = [random.randint(1000,9999) for i in range(5)]
        vals.sort(key = lambda x: random.random())
        self.values = random.choices(vals, [0.6, 0.2, 0.1, 0.05, 0.05], k=100)
        self.majority_tag = str(vals[0])

    def spawn(self):
        col = Colors.random()
        for i,v in enumerate(self.values):
            editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(i % 10 -4.5, i // 10 - 4.5, 0.7), scale = (0.7,0.7,1), rfid_tag=str(v), material=SpawnableMaterials.SimpleColor, color = col, is_temp=True)
        #((v + random.randint(-20,20))%230,(v + random.randint(-20,20))%255,(v + random.randint(-20,20))%200)

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(center = (0,0,0), extends=(25,25,16))

#editor.spawn_entity(SpawnableEntities.ProximitySensor,"rfidSensor",location = (0,0,0))
editor.spawn_entity(SpawnableEntities.InputBox,"result",location = (0,0,3))
editor.spawn_entity(SpawnableEntities.RangeFinder,"scanA",location = (-4.5, -5.25, 2.05), rotation = (-90.0, 0.0, 180.0))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"posA",location = (-4.5, -6.0, 2.0))

        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def found_majority():
    s = GoalState.Open
    user_val = ""
    try:
        user_val = InputBox.first().get_text()
    except:
        user_val = ""
        
    if len(user_val) >= 4:
        s = GoalState.Success if user_val == data.majority_tag else GoalState.Fail
    return s
def maj_goal(goal_name:str):
    editor.set_goal_state(goal_name, found_majority())

editor.set_goals_intro_text("Every cube has a random RFID tag.")
editor.specify_goal("maj_goal","Find the majority RFID tag \(the tag that at least 50% of cubes have\). Enter the result into the InputBox.", maj_goal)
TIME_LIMIT = 100.0
def time_goal(goal_name: str):
    
    if editor.get_goal_state(goal_name) == GoalState.Success:
        return
    t = max(0,TIME_LIMIT-SimEnvManager.first().get_sim_time())
    msg = f"Finish in under {int(TIME_LIMIT)} seconds. Time Remaining: {t:.2f}"
    

    if found_majority() == GoalState.Success:
        if t > 0:
            editor.set_goal_state(goal_name,GoalState.Success, msg)
    elif t <= 0:
        editor.set_goal_state(goal_name,GoalState.Fail, msg)
    else:
        editor.set_goal_state(goal_name,GoalState.Open, msg)
        
editor.specify_goal("time_goal", f"Finish in under {int(TIME_LIMIT)} seconds.", time_goal, 0, True, True)
### END GOAL CODE ###



### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    platform = MovablePlatform.first()
    platform.editor_set_rotation_limits([0,0,0])
    platform.editor_set_location_limits([11,11,0])
    platform.editor_set_movement_speed(60)
    platform.attach_entities()
    data.reset()
    data.spawn()
    RangeFinder.first().editor_set_can_read_rfid_tags(True)
    InputBox.first().set_text("")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
