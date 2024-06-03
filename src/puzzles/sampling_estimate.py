### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import numpy as np
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.pdf:List[float] = []
        self.user_percentage = -1.0

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.InfinitePlane)
editor.spawn_entity(SpawnableEntities.ObjectSpawner, "spawner", location=(2, -10, 4), rotation=(0,0,-90))
editor.spawn_entity(SpawnableEntities.TriggerZone, "CubeScanner", location=(2, -10, 0.1), scale=(9,9,1))
editor.spawn_entity(SpawnableEntities.InputBox, "Result", location=(2, -10.2, 4))

def spawn_next():
    samples:np.ndarray = np.random.choice(["Red","Green","Blue"], 50, p=data.pdf, replace=True)

    editor.destroy_temporaries()
    
    for s in samples:
        editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, color = str(s), simulate_physics=True, scale = 0.2, location = (2+random.uniform(-2,2), -10+random.uniform(-2,2), 2.4+random.uniform(-1,1)), is_temp = True, rfid_tag = str(s), adjust_coll = True)
    
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def sampling_goal(goal_name: str):
    if data.user_percentage >= 0:
        diff = abs(data.user_percentage - data.pdf[0])
        if diff <= 0.0009:
            editor.set_goal_state(goal_name, GoalState.Success, f"Correct! The true distribution is [red](Red {data.pdf[0]:.1%}) ; [green](Green {data.pdf[1]:.1%}) ; [blue](Blue {data.pdf[2]:.1%})")
            print()
        elif diff > 0.1:
            editor.set_goal_state(goal_name, GoalState.Fail)
        else:
            editor.set_goal_state(goal_name, GoalState.Open)
            new_prog = clamp((0.1-diff)*10,0,0.999)
            new_prog = new_prog*new_prog
            editor.set_goal_progress(goal_name,new_prog)

editor.set_goals_intro_text("This object spawner contains millions of cubes, comprised of an unkown number of [red](red), [green](green) and [blue](blue) cubes. You goal is to estimate the percentage of [red](red) cubes. For example, if there were 50 red, 10 green and 0 blue cubes in there, the percentage of red would be 83.3 % ( or 0.833 ). You can spawn 50 cubes at random how often you like.")
editor.specify_goal("sampling_goal", "Estimate the percentage of red cubes with a precision of at least 1 decimal digits.", sampling_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["Why is this level called 'The Law of Large Numbers'?", "What is the law of large numbers?"], "The Law of Large Numbers states that the more random samples you draw, the closer the average of those samples will be to the true average. Or more formally, the sample mean converges to the true mean.")
editor.add_hint(1,["Great, but what does that mean here?"], "It means that spawning 50 random cubes once is probably not enough to calculate the frequency of red cubes within the required margins. You need to spawn those 50 cubes many times and continuously update your estimate.")

### END HINTS ###


def on_input(box, gt, val:str):
    try:
        val = val.replace(",",".").replace("%","").replace("-","").strip()
        fval = abs(float(val))
        if fval > 1:
            fval *= 0.01
        data.user_percentage = fval
    except:
        print(f"You entered {val}, which does not look like a valid percentage.")


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    InputBox.first().on_changed(on_input)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    #recreate distribution
    data.reset()
    pdf = [random.random(),random.random(),random.random()]
    data.pdf = [p/sum(pdf) for p in pdf]
    


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    #print(f"{entity_type=}, {entity_name=}, {command=}")
    if entity_name == "spawner" and command == "Spawn":
        spawn_next()

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
