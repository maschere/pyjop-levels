### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random

### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.correct_instructions = "UUUUURRRRRPDDDDDLLLLL"
        self.player_crane_commands = []
        self.cargo_delivered = -0.01 # this is substracted from the goal progress and set to 0 when kill zone triggers with cargo

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.GrasslandOutdoor)
editor.spawn_entity(SpawnableEntities.TriggerZone, "drop_zone", location=(0, 0, 0), scale=(2.0, 2.0, 1))
editor.spawn_entity(SpawnableEntities.AirliftCrane, "crane", location=(0, 0, 5))

editor.spawn_entity(SpawnableEntities.DataExchange, "control_center", location=(5, 3, 0))


def spawn_temp_object():
    editor.spawn_static_mesh(SpawnableMeshes.TireWheel, "tire", location=(5, -5, 1), rotation=(90, 0, 0), simulate_physics=True, is_temp=True)

    
def generate_instruction_sets(cargo_x, cargo_y, max_instructions=26): # cargo_x and cargo_y for possible generation of correct paths
    
    # This could also generate a random correct path, not yet called anywhere
    def select_correct_path():
        data.correct_instructions = random.choice([
        "RURUUURRRRULLDDDDLLLLDLLRR",
        "LUUURRRUULRRRRDDDDLLLLLDDU"
        "URURRRRRLLRUUULLDLDLDLDDLR"    
        ])

    def generate_incorrect_path():
        path = []
        for _ in range(max_instructions):
            path.append(random.choice(['L', 'R', 'U', 'D']))
        return path


    # Generate nine incorrect paths
    instruction_sets = []
    instruction_sets.append(data.correct_instructions) # Replace with select_correct_path()
    while len(instruction_sets) < 10:
        instruction_sets.append(generate_incorrect_path())

    # Shuffle the instruction sets 
    random.shuffle(instruction_sets)

    return instruction_sets


def handle_overlap(t,simtime,trigg_data):
    if trigg_data.entity_name == "tire":
        print("debug log: tire dropped to drop zone")
        data.cargo_dropped = 0.01 # This signals that the cargo is dropped and adjusts goal progress
        

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("There are crane instruction sets in the data exchange. Select the one that returns the crane to the "
                           " start point/drop zone (0,0) and move the crane according to the instructions in the correct set")

def get_progress():
    correct_command_count = 0
    for i in range(len(data.player_crane_commands)):
        if data.player_crane_commands[i] == data.correct_instructions[i]:
            correct_command_count += 1
        else: editor.set_goal_state("levelGoal", GoalState.Fail)
        
    return correct_command_count / len(data.correct_instructions)
    
def level_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        get_progress() + data.cargo_delivered , #minus cargo delivered (0.01) for also finally checking the cargo collision with drop zone
        f"Follow the crane instructions that return the cargo to the drop zone",
    )

editor.specify_goal("levelGoal", "Follow the crane instructions that return the cargo to the starting position/drop zone at 0,0", level_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###


def begin_play():
    print("begin play")
    AirliftCrane.first().editor_set_shake_intensity(0) # Shaking causes inaccuracies tracking the location

    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    editor.set_goal_state("levelGoal", GoalState.Open)
    data.reset()
    spawn_temp_object()
    trigg = TriggerZone.first()
    trigg.on_triggered(handle_overlap) 

    # setup cargo location and generate crane instruction sets to data exchange    
    cargo_x, cargo_y = 5, -5
    instruction_sets = generate_instruction_sets(cargo_x, cargo_y)

    for i, instructions in enumerate(instruction_sets):
        DataExchange.first().set_data(f"Instruction set {i+1}",''.join(instructions) )
    
    

editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_name == "crane" and command == "setTargetLocation": 
        # Extract player commanded coordinate values for the crane
        new_x = float(val.array_data[0][0])
        new_y = float(val.array_data[0][1])
        # add player move commands to data.player_crane_commands to evaluate if they match with correct instructions
        # This may require a bit more sophisticated approach, there seems to be maybe a rounding issue after player picks up cargo and uses setTargetLocation
        if new_x > list(editor.get_location("crane"))[0]:
            data.player_crane_commands.append("R")
            
        elif new_x < list(editor.get_location("crane"))[0]:
            data.player_crane_commands.append("L")
            
        elif new_y < list(editor.get_location("crane"))[1]:
            data.player_crane_commands.append("U")
            
        elif new_y > list(editor.get_location("crane"))[1]:
            data.player_crane_commands.append("D")
    
    elif entity_name == "crane" and command =="pickup":
        data.player_crane_commands.append("P")

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    # Airlift Crane doesn't have built-in getter for location. Lets send it to data exchange but round to closest integer
    crane_location = list(editor.get_location("crane"))
    rounded_location = [round(val, 0) for val in crane_location]
    DataExchange.first().set_data("crane_location", rounded_location)
    sleep(0.3)



editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#this template code will be provided to the player
#add level specific hints or boilerplate code here.


env = SimEnvManager.first()

while SimEnv.run_main():
    pass
