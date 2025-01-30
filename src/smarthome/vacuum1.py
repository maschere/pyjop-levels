### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###
SCALE_DIV = 2.0
N = 15
### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.time_counter = 0.0
        self.dirt_count = 0
        self.mypath:list[Vector3] = []
        self.robot_start = Vector3(0,0,0)

    def spawn_maze(self):
        i = 1
        j = random.randint(1,3)
        self.mypath = [Vector3(i,j,0)]
        for _ in range(N*5):
            x = 0
            y = 0
            if random.random() > 0.5:
                x = random.choice((-1,1,1,1))
            else:
                y = random.choice((-1,1,1))
            i2 = i+x
            j2 = j+y
            if i2 < 1 or j2 < 1 or i2 > N-2 or j2 > N-2:
                continue
            i = i2
            j = j2
            if Vector3(i2,j2,0) not in self.mypath:
                self.mypath.append(Vector3(i2,j2,0))
    
        for i in range(N):
            for j in range(N):
                if Vector3(i,j,0) not in self.mypath:
                    editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(i/SCALE_DIV,j/SCALE_DIV, 0), scale = 0.5/SCALE_DIV, material=SpawnableMaterials.SimpleColor, color = 0.03, is_temp=True)

        self.robot_start = self.mypath[0] / SCALE_DIV
        #place robot
        editor.set_location("vac", self.robot_start)
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it often makes sense to call this function on each level reset to respawn the temp objects in their original location.
        for p in self.mypath:
            if random.random() > 0.5:
                self.dirt_count += 1
                editor.spawn_static_mesh(SpawnableMeshes.DirtPile, location=(p.x/SCALE_DIV,p.y/SCALE_DIV, 0), is_temp = True, scale=(random.uniform(0.2,0.5),random.uniform(0.2,0.5),0.4), rotation=Rotator3(0,0,random.uniform(-180,180)), rfid_tag="Dirt")
        
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MinimalisticIndoor)
editor.spawn_entity(SpawnableEntities.VacuumRobot, "vac", location=(0.1+1/SCALE_DIV, 0.1+1/SCALE_DIV, 0))


### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Program this easy to use vacuum cleaner robot to clean up all dirt and return it to its starting location.")

def dirt_goal(goal_name: str):
    if data.dirt_count <=0:
        editor.set_goal_progress(goal_name,0)
        return
    editor.set_goal_progress(
        goal_name,
        VacuumRobot.first().get_dirt_count() / data.dirt_count,
        f"Cleanup all dirt: {VacuumRobot.first().get_dirt_count()} / {data.dirt_count}.",
    )

def return_goal(goal_name: str):
    if data.dirt_count <= 0 or VacuumRobot.first().get_dirt_count() < data.dirt_count:
        editor.set_goal_state(goal_name, GoalState.Open)
        return
    dis = (editor.get_location("vac") - data.robot_start).length
    prog = 1.0 if dis < 0.21 else clamp(1.0 - (dis-0.209),0.0,0.99)
    editor.set_goal_progress(goal_name, prog)

editor.specify_goal("dirt_goal", "Cleanup all dirt.", dirt_goal, 0.8, hide_next=False)
editor.specify_goal("return_goal", "Return to the robot's starting location.", return_goal, 0.2, hide_next=False)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
# editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")

# def select_conveyor(gt:float, num:int, num_revealed:int):
#     editor.change_hint(num, "Here it is!")
#     ConveyorBelt.find("belt1").focus()
# editor.add_hint(3,["Where is the conveyor belt?"], on_reveal=select_conveyor)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    data.spawn_maze()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
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
