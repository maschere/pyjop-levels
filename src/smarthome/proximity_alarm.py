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
        self.last_changed:dict[str, float] = {}
        self.should_sound_alarm_at = -10.
        self.should_disable_alarm_at = -10.
        self.sounded_alarm_at = -10.
        self.disabled_alarm_at = -10.
        self.last_spawn_at = -1.
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MuseumHall)

editor.spawn_entity(SpawnableEntities.AlarmSiren, "alarm", location=(-1.15, -4.45, 5.85), rotation=(0.0, 0.0, 90.0))
editor.spawn_entity(SpawnableEntities.ProximitySensor, "proximity", location=(0.0, -3.2, 0))
editor.spawn_static_mesh(SpawnableMeshes.PaintingWide, location=(0, -4.47, 2.85))
def spawn_next_walker():
    npcname = "".join(random.choices("yxcvbnmasdfghjklqwertzuio1234567890_", k=5)) + ("EMPLOYEE" if random.random()>0.8 else "GUEST") + "".join(random.choices("yxcvbnmasdfghjklqwertzuio1234567890_", k=5))
    editor.spawn_entity(SpawnableEntities.HumanoidRobot, npcname, location=(random.randint(-4,4), random.randint(-2,7), 2), is_temp=True, is_readable=False, is_controllable=False, is_clickable=False)
    
    # editor.set_clickable(npcname, False)
    # editor.set_controllable(npcname, False)
    # editor.set_readable(npcname, False)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def alarm_goal(goal_name: str):
    s = GoalState.Open
    txt = "Sound the alarm if a GUEST is within 2m of the ProximitySensor."
    if data.sounded_alarm_at > 0 and data.should_sound_alarm_at > 0:
        if data.sounded_alarm_at > data.should_sound_alarm_at + 1.1:
            s = GoalState.Fail
            txt = "You did not sound the alarm in time. Please reset."
        else:
            s = GoalState.Success
    elif data.sounded_alarm_at > 0:
        s = GoalState.Fail
        txt = "FALSE ALARM. Please reset."
    elif data.should_sound_alarm_at > 0:
        left = max(0.0, data.should_sound_alarm_at + 1.1 - SimEnvManager.first().get_sim_time())
        if left <= 0:
            s = GoalState.Fail
            txt = "You did not sound the alarm in time. Please reset."
        elif data.sounded_alarm_at < 0:
            txt = f"Sound the alarm if a GUEST is within 2m of the ProximitySensor. SECURITY BREACH {left:.2}s left to sound alarm!"
        
    editor.set_goal_state(goal_name, s, txt)

editor.set_goals_intro_text("An expensive artwork is on display here. Only EMPLOYEEs are allowed within 1m of the artwork. A proximity sensor allows you to check everyone in range.")
editor.specify_goal("alarm_goal", "Sound the alarm if a GUEST is within 1m of the ProximitySensor.", alarm_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["What is 2+4?","What is 2*3?"], "The result is 6.")

def select_conveyor(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, "Here it is!")
    ConveyorBelt.find("belt1").focus()
editor.add_hint(3,["Where is the conveyor belt?"], on_reveal=select_conveyor)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "setAlarmEnabled":
        is_enabled = val.get_bool()
        if is_enabled and data.sounded_alarm_at < 0:
            data.sounded_alarm_at = gametime
        elif is_enabled==False and data.disabled_alarm_at < 0:
            data.disabled_alarm_at = gametime

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    if data.sounded_alarm_at > 0 or data.should_sound_alarm_at > 0:
        return
    walkers = HumanoidRobot.find_all(suppress_warnings=True)
    is_alarm = False
    for walker in walkers:
        if walker.entity_name not in data.last_changed or (random.random() > 0.3 and data.last_changed[walker.entity_name] < simtime - 5) or walker.get_is_blocked():
            walker.set_walking(random.uniform(0,360), random.uniform(0.4,1))
            data.last_changed[walker.entity_name] = simtime
        loc = editor.get_location(walker.entity_name)
        if "GUEST" in walker.entity_name and (loc - (0.0, -3.2, 0.0)).length < 2:
            is_alarm = True
            if data.should_sound_alarm_at < 0:
                data.should_sound_alarm_at = simtime

    if not is_alarm and data.should_sound_alarm_at > 0 and data.should_disable_alarm_at < 0:
        data.should_disable_alarm_at = simtime

    if is_alarm == False and data.last_spawn_at + 7 + random.random() < simtime:
        data.last_spawn_at = simtime
        spawn_next_walker()
        


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
while SimEnv.run_main():
    pass
