### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
from datetime import datetime
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.time_in_sync = 0.0
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)
editor.spawn_static_mesh(SpawnableMeshes.Table)
editor.spawn_entity(SpawnableEntities.AlarmClock, "clock", location=(0, 0, 1), rotation=(-15,0,0), scale = 4)

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def sync_goal(goal_name: str):

    editor.set_goal_progress(
        goal_name,
        data.time_in_sync/10.0,
    )
editor.specify_goal("sync_goal", "Sync the alarm clock to your system time.", sync_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
# editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")
# def select_conveyor(gt:float, num:int, num_revealed:int):
#     editor.change_hint(num, "Here it is!")
#     ConveyorBelt.find("belt1").focus()
# editor.add_hint(1,["Where is the conveyor belt?"], on_reveal=select_conveyor)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    on_reset()
    
    


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    data.reset()
    c = AlarmClock.first()
    c.set_current_time(random.random()*23.8)
    c.set_is_running(False)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###



### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    c = AlarmClock.first()
    h,m,s = c.get_current_time().split(":")
    total_sec = int(s) + 60 * int(m) + 3600 * int(h)
    

    # Get the current system time
    current_time = datetime.now()

    # Calculate the time difference from midnight
    midnight = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    total_sec2 = (current_time - midnight).total_seconds()
    if abs(total_sec2-total_sec) < 1.9:
        data.time_in_sync += deltatime
    else:
        data.time_in_sync = 0


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
