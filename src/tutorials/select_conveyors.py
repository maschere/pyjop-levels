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
        self.delivered:set[str] = set()
        self.active_belts:set[str] = set()

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.MinimalisticIndoor)
for i in range(7):
    editor.spawn_entity(SpawnableEntities.ConveyorBelt, f"_entityConveyor{i}", location=(0, (i-3)*2, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "_entityTrigger0", location = (4.1,0,0), scale = (1,15,3))
editor.spawn_entity(SpawnableEntities.TriggerZone, "_entityTrigger1", location = (-4.1,0,0), scale = (1,15,3))
def spawn_temp_object():
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it makes sense to call this function on each level reset to respawn the temp objects in their original location.
    editor.spawn_entity(SpawnableEntities.Deliverable, "box0", location=(0.7,(random.randint(0,6)-3)*2, 3), is_temp = True)
    sleep(0.4)
    editor.spawn_entity(SpawnableEntities.Deliverable,"box1", location=(-0.7, (random.randint(0,6)-3)*2, 3.3), is_temp = True)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def deliver_goal(goal_name: str):
    if len(data.active_belts) <= 2:
        editor.set_goal_progress(
            goal_name,
            len(data.delivered) / 2,
            "Drop off the boxes in front or behind of the conveyor belts. You may activate [red](at most 2) conveyor belts!"
        )
    else:
        editor.set_goal_state(goal_name, GoalState.Fail, "You have activated more than 2 conveyor belts. That is not allowed. Please reset and try again!")
editor.set_goals_intro_text("In this tutorial you need to combine what you learned from the previous two tutorials by combining a FOR loop and an IF conditional.")
editor.specify_goal("deliver_goal", "Drop off the boxes in front of or behind the conveyor belts. You may activate [red](at most 2) conveyor belts!", deliver_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
def select_conveyor(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, "Each conveyor belt has a built-in pressure sensor to check whether something is on top of it or not. Check the 'IsTransporting' field in the details window of a conveyor belt.")
    sleep(1)
    ConveyorBelt.any_random().focus()
editor.add_hint(0,["How can I check programmatically which conveyor belt is transporting something?","Is there a sensor to check whether a conveyor is transporting a box or not?"], on_reveal=select_conveyor)
### END HINTS ###



def on_deliver(trig:TriggerZone, gt:float, e:TriggerEvent):
    if e.entity_name.startswith("box") and e.entity_name not in data.delivered:
        data.delivered.add(e.entity_name)
        editor.apply_impulse(e.entity_name, (0,0,20))
        editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(e.entity_name), color = Colors.Green)
        editor.play_sound(SpawnableSounds.ExplosionPuff, location = editor.get_location(e.entity_name))
        editor.set_lifetime(e.entity_name, 1.5)
    

### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    editor.set_clickable("_entityTrigger0", False)
    editor.set_clickable("_entityTrigger1", False)
    editor.set_hidden("_entityTrigger0", True)
    editor.set_hidden("_entityTrigger1", True)
    SmartSpeaker.first().set_sound_by_name(BuiltinMusic.DemoPlaylist)
    for t in TriggerZone.find_all():
        t.on_triggered(on_deliver)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset() # reset data model
    editor.set_goal_state("deliver_goal", GoalState.Open)
    spawn_temp_object()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_type == "ConveyorBelt" and command == "setTargetSpeed":
        data.active_belts.add(entity_name)
        if len(data.active_belts) > 2:
            print("Too many conveyor belts are running! Only use 2.", col=Colors.Red)

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###


editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")

### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###

### PLAYER TEMPLATE CODE ###
# In this tutorial you need to combine what you learned in the previous two tutorials:
# iterate all conveyor belts, check each belt if it is transporting something or not and then set the speed > 0 if (and only if) that is True