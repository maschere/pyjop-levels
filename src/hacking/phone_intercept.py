### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import re
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.last_number = ""
        self.user_number = ""
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.CellarHallway)
editor.spawn_entity(SpawnableEntities.DialupPhone, "BuggedPhone", location=(3, -11, 0))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

def new_num_goal(goal_name: str):
    if data.last_number:
        editor.set_goal_state(goal_name, GoalState.Success)
def num_goal(goal_name: str):
    if not data.user_number:
        s = GoalState.Open
    elif data.last_number == data.user_number:
        s = GoalState.Success
    else:
        s = GoalState.Fail
    editor.set_goal_state(goal_name, s)
        
editor.set_goals_intro_text("We have bugged the red phone booth to be able to intercept which number is being dialed.")

editor.specify_goal("new_num_goal", "Press reset to intercept a new number.", new_num_goal,goal_value=0.1)
editor.specify_goal("num_goal", "What 7 digit phone number was just dialed on the bugged phone? Once you found out, dial the same numbers again.", num_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["The numbers mason, what do they mean?","What are all those thousands upon thousands of numbers?"], "That data is the raw waveform audio data of the dial-tones you heard. If you convert all those numbers to a .wav file and play it back, you will hear the exact same sequence of dial-tones.")
editor.add_hint(1,["How can I approach this?","How could I possibly match that raw audio data to the corresponding dial number?"], "While the interception is slightly noisy, the raw dial tone audio for 5 (for example) will always result in approximately the same numbers. So you could dial each individual number from 0-9 once and save the corresponding audio signal in a kind of lookup database. Then try to find the nearest matches for the intercepted number.")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    SmartSpeaker.first().set_volume(0)


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    data.last_number = "".join([str(random.randint(0,9)) for i in range(7)])
    sleep(1)
    DialupPhone.first().dial_number(data.last_number)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if gametime > 1.5 and entity_name == "BuggedPhone" and command == "DialNumber":
        number = val.get_string()
        if re.fullmatch("\\d{7}", number):
            data.user_number = number

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

# set editor template code
#editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#this template code will be provided to the player
#add level specific hints or boilerplate code here.
print("hello world")
