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
        self.hint = random.choice([9614, 10725, 11520, 1194, 11550, 11088, 11720])
        self.correct_pin = None
        self.reset_required = False # flag if player has already tried a pin and failed
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MuseumHall)
editor.spawn_entity(SpawnableEntities.PinHacker, "safe", location=(-0.000,-3.750,0.000), rotation=(0.000,0.000,90.000), scale=(1.500,1.500,1.500)) #generated-code
editor.spawn_entity(SpawnableEntities.DataExchange, "pc", location=(5.350,-1.800,0.000), rotation=(0.000,0.000,90.000)) #generated-code
editor.spawn_entity(SpawnableEntities.InputBox, "pin_input", location=(-0.5, -3.5, 2.0))


def on_input(sender,simtime,new_text):
    print(f"Trying to unlock with: {new_text}")
    if int(new_text) == data.correct_pin and data.reset_required == False:
        editor.set_goal_state("crack_safe_goal", GoalState.Success)
    else:
        print("Invalid PIN!, Reset the level!")
        data.reset_required = True
        editor.set_goal_state("crack_safe_goal", GoalState.Fail)
        

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Get the PIN hint from the computer and crack the safe using the input box. You have only one attempt before the safe goes to emergency lockdown")

def sample_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        0,
        f"Crack the safe",
    )

editor.specify_goal("crack_safe_goal", "Crack the safe", sample_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
def select_inputbox(gt:float, num:int, num_revealed:int):
    InputBox.first().focus()
editor.add_hint(0,["How do I input the correct pin?"], "Use the InputBox to input the pin either by code or manually clicking and typing", on_reveal=select_inputbox)


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    InputBox.first().on_changed(on_input)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###

def sum_of_prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return sum(factors)



def on_reset():
    print("Level resetting")
    data.reset()
    DataExchange.first().set_data("Hint", "Sum of prime factors")
    DataExchange.first().set_data("PIN", data.hint)
    # InputBox.first().editor_set_hint_text("Enter the correct pin")  THIS SEEMS TO TRIGGER THE PLAYER INPUT EVENT RANDOMLY
    data.correct_pin = sum_of_prime_factors(data.hint)
    # print(f"Debug: editor has set the correct pin: {data.correct_pin}")


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


env = SimEnvManager.first()

while SimEnv.run_main():
    # main loop to retrieve data from the SimEnv, calculate stuff and send commands back into the SimEnv
    # for example, get current time and display it
    pass
