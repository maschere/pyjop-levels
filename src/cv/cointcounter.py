### INIT CODE - DO NOT CHANGE ###
from pyjop import *
from types import SimpleNamespace

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###

NUM_RUNS = 5

COINS = {
    "CoinEuro1":100,
    "CoinEuro2":200,
    "CoinEuroCent1":1,
    "CoinEuroCent2":2,
    "CoinEuroCent5":5,
    "CoinEuroCent10":10,
    "CoinEuroCent20":20,
    "CoinEuroCent50":50
}

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.num_sum_correct = 0
        self.num_count_correct = 0


    def spawn_next(self):
        editor.destroy_temporaries()
        sleep()
        self.sum = 0
        self.count = random.randint(7,16)
        #print(self.count)
        idx = sorted(list(range(16)), key=lambda x: random.random())[0:self.count]
        
        for i in range(0, 16):
            if i not in idx:
                continue
            cname,cval = random.choice(list(COINS.items()))
            self.sum += cval
            x = (i % 4 - 1.5) / 1.5  * 1.2
            y = (i //4 - 1.5) / 1.5  * 1.2
            editor.spawn_static_mesh(SpawnableMeshes(cname), simulate_physics=True, is_temp=True, location = (5.000 + x + random.uniform(-0.15,0.15),0.150 + y + random.uniform(-0.15,0.15),0.3 + random.uniform(0,.2)), rotation = (0,0 if random.random()>0.5 else 180, random.uniform(-180,180)), scale=2)

        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)
editor.spawn_entity(SpawnableEntities.SmartCamera, "cam", location=(4.85, 0.15, 3.75), rotation=(0,-90,0))

editor.spawn_entity(SpawnableEntities.InputBox, "CoinCount", (1.5,-1,0.3))
#editor.spawn_entity(SpawnableEntities.InputBox, "CoinSum", (1.5,0,0.5))
editor.spawn_static_mesh(SpawnableMeshes.Cube, scale= (3.5,3.5,0.2), location=(5, 0.15, 0), material=SpawnableMaterials.SimpleColor, color=Colors.Green)




        
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
editor.set_goals_intro_text(f"Let's build a coin counting machine. Use the camera to count how many coins are visible in the image. Enter the result in the InputBox. Do this {NUM_RUNS} times.")
editor.specify_goal("CoinCount", "How many coins are there?", None, 1, hide_next=False)
#editor.specify_goal("CoinSum", "What is the total sum (in Euro Cents) of all coins?", None, 1, hide_next=False)

### END GOAL CODE ###


# ### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
# editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")
# def select_conveyor(gt:float, num:int, num_revealed:int):
#     editor.change_hint(num, "Here it is!")
#     ConveyorBelt.find("belt1").focus()
# editor.add_hint(1,["Where is the conveyor belt?"], on_reveal=select_conveyor)
# ### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_input(box:InputBox,gt:float,txt:str):
    val = -1
    if txt != "":
        try:
            val = int(txt)
            assert(val>=0)
        except:
            print(f"{txt} is not a valid integer number > 0", col=Colors.Red)
            return
    if box.entity_name == "CoinCount" and data.count == val:
        data.num_count_correct += 1
        prog = data.num_count_correct / NUM_RUNS
        editor.set_goal_progress(box.entity_name, prog)
        if prog < 1:
            data.spawn_next()
        return
    elif box.entity_name == "CoinSum" and data.sum == val:
        data.num_sum_correct += 1
        prog = data.num_count_correct / NUM_RUNS
        editor.set_goal_progress(box.entity_name, prog)
        if prog < 1:
            data.spawn_next()
        return
    if txt.strip() != "":
        print(f"{txt} is not correct...", col=Colors.Red)
            

    
        

def begin_play():
    print("begin play")
    for inp in InputBox.find_all():
        inp.on_changed(on_input)
    on_reset()

editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    cam = SmartCamera.find("cam")
    cam.set_fov(52)
    data.reset()
    data.spawn_next()
    
    for inp in InputBox.find_all():
        #on_input(inp, 0, "-1")
        inp.set_text("")
        inp.editor_set_hint_text(f"Enter {inp.entity_name}...")
        editor.set_goal_progress(inp.entity_name,0.0)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


# ### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
# def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
#     if command == "setData":
#         data.predict_count += 1

# editor.on_player_command(on_player_command)
# ### END ON PLAYER COMMAND CODE ###

# ### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
# def on_tick(simtime: float, deltatime: float):
#     pass

# editor.on_tick(on_tick)
# ### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
