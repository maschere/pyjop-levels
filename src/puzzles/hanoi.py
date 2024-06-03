### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.source_pole:int = 0

data = DataModel()


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.spawn_entity(SpawnableEntities.AirliftCrane, "crane", location=(0, 0, 2.5))
NUM_DISKS = 4
POLES_X = (-3,0,3)
for i in POLES_X:
    editor.spawn_static_mesh(SpawnableMeshes.Cylinder, location=(i, 0, 1), scale = (0.2,0.2,2.2), material=SpawnableMaterials.SimpleColor, color = Colors.Brown)
data.source_pole = 0
def spawn_disks():
    for i in range(NUM_DISKS):
        editor.spawn_static_mesh(SpawnableMeshes.Torus, f"disk_{i}", location=(POLES_X[data.source_pole], 0, 8-i/2), scale = (0.6+i/(NUM_DISKS+3), 0.6+i/(NUM_DISKS+3), 1), simulate_physics=True, is_temp=True, material=SpawnableMaterials.SimpleColor, color = get_color_from_map(Colormaps.gist_rainbow,i/(NUM_DISKS-1)))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def hanoi_goal(goal_name: str):
    if SimEnvManager.first().get_sim_time() < 4:
        return
    if AirliftCrane.first().get_is_transporting():
        return
    disks:List[List[int]] = [[],[],[]]
    locs = [(i,editor.get_location(f"disk_{i}")) for i in range(NUM_DISKS-1,-1,-1)]
    locs.sort(key=lambda x: x[1].z)
    for i,l in locs:
        if l.z < 0.7 and (l.y < -0.2 or l.y > 0.2 or l.x < -3.2 or l.x > 3.2):
            print("You must put all disks onto one of the rods.", col=Colors.Red)
            sleep(2) #stop for an invalid config
            SimEnvManager.first().reset(True)
            return
        if l.x > -3.3 and l.x < -2.7 and l.z < 2:
            disks[0].append(i)
        elif l.x > -0.3 and l.x < 0.3 and l.z < 2:
            disks[1].append(i)
        elif l.x > 2.7 and l.x < 3.3 and l.z < 2:
            disks[2].append(i)
    #check each rod for validity
    for i in range(3):
        for j in range(1,len(disks[i])):
            if disks[i][j] > disks[i][j-1]:
                print("You cannot put a larger disk on top of a smaller one.", col= Colors.Red)
                sleep(2) #stop for an invalid config
                SimEnvManager.first().reset(True)
                return

    #all is valid, check if one stack is complete
    max_len = max(len(disks[1]), len(disks[2]))
 
    editor.set_goal_progress(
        goal_name,
        max_len/NUM_DISKS
    )

editor.specify_goal("hanoi_goal", "Move all disks to one of the other rods. You may never put a larger disk on top of a smaller one!", hanoi_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["What is puzzle game called?","This seems familiar. What's the name of this challenge?"], "This puzzle game is called Towers of Hanoi. It's a famous puzzle invented by French mathematician Edouard Lucas in 1883.")

editor.add_hint(2,["Do I need recursion for this problem?","Do I solve this iteratively or recursively?"], "While Towers of Hanoi can be solved either iteratively or recursively, the recursive solution is a lot shorter and easier to understand for most.")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    AirliftCrane.first().editor_set_shake_intensity(0.1)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    spawn_disks()
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
