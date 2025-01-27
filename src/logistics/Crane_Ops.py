### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random

### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
MAX_POS = 5
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.target_location = Vector3(random.randint(3,MAX_POS)*random.choice([-1,1]),random.randint(3,MAX_POS)*random.choice([-1,1]),0)
        self.cargo_delivered = False #
        self.command_count:int = 0
        self.instructions_sets = self.make_instruction_sets()

    def make_instruction_sets(self) -> list[str]:
        ins:list[str] = []
        found_way = False
        for _ in range(3000):
            current_ins:list[str] = []
            found_target = False
            pos = Vector3()
            for i in range(random.randint(3,51)):
                #make rand move
                m = random.choice("LRFB")
                if pos.x >= MAX_POS+1:
                    m = "B"
                if pos.x <= -MAX_POS+1:
                    m = "F"
                if pos.y >= MAX_POS+1:
                    m = "L"
                if pos.y <= -MAX_POS+1:
                    m = "R"
                current_ins.append(m)
                if m == "L":
                    pos.y -= 1
                if m == "R":
                    pos.y += 1
                if m == "F":
                    pos.x += 1
                if m == "B":
                    pos.x -= 1
                if pos.x == self.target_location.x and pos.y == self.target_location.y:
                    found_target = True
                    current_ins.append("P")
                if found_target and pos.x == 0 and pos.y == 0:
                    #print(f"found way: {''.join(current_ins)}")
                    found_way = True
                    break # found back
            if not found_target and pos.x == 0 and pos.y == 0:
                current_ins.append(random.choice("LRFB"))
            if not found_target and abs(pos.x) > 2 and abs(pos.y) > 2:
                current_ins[random.randrange(1,len(current_ins)-2)] = "P"
            ins.append("".join(current_ins))
        if not found_way:
            x_cmds = ["F"] * abs(int(self.target_location.x))
            if self.target_location.x < 0:
                x_cmds = ["B"] * abs(int(self.target_location.x))
            y_cmds = ["R"] * abs(int(self.target_location.y))
            if self.target_location.y < 0:
                y_cmds = ["L"] * abs(int(self.target_location.y))
            cmds = x_cmds + y_cmds
            random.shuffle(cmds)
            x_cmds = ["B"] * abs(int(self.target_location.x))
            if self.target_location.x < 0:
                x_cmds = ["F"] * abs(int(self.target_location.x))
            y_cmds = ["L"] * abs(int(self.target_location.y))
            if self.target_location.y < 0:
                y_cmds = ["R"] * abs(int(self.target_location.y))
            cmds_back = x_cmds + y_cmds
            random.shuffle(cmds_back)
            cmds.append("P")
            ins[5] = "".join(cmds + cmds_back)
            #print("adding manual way")
                
        #print(f"{ins[-1]}")
        random.shuffle(ins)
        return ins

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.GrasslandOutdoor)
editor.spawn_entity(SpawnableEntities.TriggerZone, "drop_zone", location=(0, 0, 0), scale=(1.0, 1.0, 1))
editor.spawn_entity(SpawnableEntities.AirliftCrane, "crane", location=(0, 0, 3))

editor.spawn_entity(SpawnableEntities.DataExchange, "control_center", location=(7, 7, 0))


def spawn_temp_object():
    editor.spawn_static_mesh(SpawnableMeshes.TireWheel, "tire", location=data.target_location + (0,0,1), rotation=(90, 0, 0), scale=0.6,simulate_physics=True, is_temp=True)

def handle_overlap(t,simtime,trigg_data):
    if trigg_data.entity_name == "tire":
        #print("debug log: tire dropped to drop zone")
        data.cargo_delivered = True # This signals that the cargo is dropped and adjusts goal progress
        

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###


def get_progress():
    correct_command_count = 0
    for i in range(len(data.player_crane_commands)):
        if data.player_crane_commands[i] == data.correct_instructions[i]:
            correct_command_count += 1
        else:
            print("Fail - Player commands: ", data.player_crane_commands)
            print("Correct commands: ", data.correct_instructions)
            editor.set_goal_state("levelGoal", GoalState.Fail)
            
        
    return correct_command_count / len(data.correct_instructions)
    
def level_goal(goal_name: str):
    if data.cargo_delivered:
        editor.set_goal_state(goal_name, GoalState.Success)
        return
    editor.set_goal_state(goal_name, GoalState.Open)

#editor.set_goals_intro_text("The AirliftCrane is at (0,0,3). To figure out the position of the tire, get all instruction_sets from the DataExchange. They each consist of L = left, R = right, F = forward, B = backward commands and P = pickup. A correct instruction set will return the AirliftCrane back to (0,0) after pickup.")
editor.set_goals_intro_text("The AirliftCrane is at (0,0,3). You need to figure out the location of the tire, move the crane there and pick it up, then move it back to the crane's starting location. To do that, you need to filter the instruction_sets from the DataExchange to find the correct one. They each consist of movement commands (L = 1m left, R = 1m right, F = 1m forward, B = 1m backward) and a pickup command (P). A correct instruction set will return the AirliftCrane back to (0,0) after pickup.")
editor.specify_goal("levelGoal", "Pickup the tire with the AirliftCrane and drop it in the yellow drop zone back at \(0,0\)", level_goal)
def cmd_goal(goal_name: str):
    s = GoalState.Success
    if data.command_count <= 0:
        s = GoalState.Open
    elif data.command_count > 4:
        s = GoalState.Fail
    editor.set_goal_state(
        goal_name,
        s,
        f"Issue at most 4 commands. Current command count: {data.command_count}/4"
    )
editor.specify_goal("cmdGoal", "Issue at most 4 commands. Current command count: 0/4", cmd_goal,0,True,True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
#editor.add_hint(0,["How should I solve the level?"], "There are instruction sets on the Data Exchange. Only one of them is a correct one which ends up back in the beginning (0, 0). You should create a code that reads the move instructions U=Up D=Down L=Left R=Right P=Pickup and determines what set will return to center. You should then program the crane to move accordingly. For example if there's instruction UP, the crane should move -1.0 on the Y-axis. You can get the current location of the crane from the data exchange")
               
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###


def begin_play():
    #print("begin play")
    AirliftCrane.first().editor_set_shake_intensity(0) # Shaking causes inaccuracies tracking the location
    sleep(2) # This seems to help to register the event handler correctly on first start, without needing a restart to make it work
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    AirliftCrane.first().editor_set_shake_intensity(0)
    data.reset()
    editor.set_goal_state("levelGoal", GoalState.Open)
    spawn_temp_object()
    trigg = TriggerZone.first()
    trigg.on_triggered(handle_overlap) 

    DataExchange.first().set_data(f"instruction_sets", data.instructions_sets)
    
    

editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type == "AirliftCrane":
        data.command_count += 1

editor.on_player_command(on_player_command)

# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###



env = SimEnvManager.first()

#get the instruction sets from the data exchange
instructions = DataExchange.first().get_data("instruction_sets")
#find the correct instruction set and move the crane accordingly

while SimEnv.run_main():
    pass
