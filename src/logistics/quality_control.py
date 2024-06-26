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
        self.time_counter = 0.0
        self.last_spawn_at = -999999.0
        self.last_sound_at = -999999.0 # this is to prevent playing the sound two times in a row everytime it hits trigger zone
        self.current_rotation = 0 #this is used for the turnable conveyor belt
        self.correct = 0 # for level goal 
        self.box_count = 0 #this is used to determine jams or drops to floor (too many boxes on level at once)
        
data = DataModel()

### END DATA MODEL ###

### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.SmallWarehouse)
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt1", location=(-6.55, -4.0, 0.0), scale=(1.0, 1.0, 1.206), is_controllable=False)
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt2", location=(3.600,-4.000,0.000), scale=(1.000,1.000,0.842), is_controllable=False) #generated-code

editor.spawn_entity(SpawnableEntities.TurnableConveyorBelt, "turnable_belt1", location=(-1.45, -4.0, 0.0), is_controllable=False)

editor.spawn_entity(SpawnableEntities.PushButton, "turn_button", location=(-4.25, -2.1, 2.45), rotation=(90.0, 0.0, 0.0))
editor.spawn_entity(SpawnableEntities.PushButton, "discard_button", location=(-4.25, -2.1, 1.3), rotation=(90.0, 0.0, 0.0))

editor.spawn_static_mesh(SpawnableMeshes.Cube, location = (-4.25, -2.25, 1.55), scale = (1.138, -0.218, 3.245), material = SpawnableMaterials.SimpleColor, color = ((0.25)/5,.2,.2), is_temp=False)

editor.spawn_entity(SpawnableEntities.ToggleSwitch, unique_name="belt_brake", location=(-4.15, -2.1, 1.95), rotation=(-90.0, 0.0, 180.0))
editor.spawn_entity(SpawnableEntities.ObjectSpawner, unique_name="spawner1", location=(-8.45, -3.95, 3.7), rotation=(0.0, 0.0, -90.0), is_controllable=False, is_readable=False)
editor.spawn_entity(SpawnableEntities.RangeFinder, "range_finder1", location=(-4.25,-6.000,0.000), rotation=(0.000,0.000,180.000), scale=(1.000,1.000,1.876)) 
editor.spawn_static_mesh(SpawnableMeshes.PalletBoxOpen, location=(-1.45, 1.0, 0.0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "discard_zone", location=(-1.450,1.050,1.400), scale=(1.395,1.107,0.163)) #generated-code
editor.spawn_entity(SpawnableEntities.MovablePlatform, "platform1", location=(-1.40,-1.20,0.5), is_controllable=False) 
editor.spawn_entity(SpawnableEntities.DeliveryContainer, "container1", location=(7.250,-4.000,0.000)) #generated-code

def spawn_next():
    if SimEnvManager.first().get_sim_time() - data.last_spawn_at < 15:
        return
    data.last_spawn_at = SimEnvManager.first().get_sim_time()
    
    # box quality
    quality = random.choices(["ok", "defected"], weights=[45, 55], k=1)[0]
    
    editor.spawn_entity(SpawnableMeshes.Deliverable, f"Box_{random.randint(0,999999)}", rfid_tag = f"Box_{quality}", location=(-8.5, -3.95, 2.9), scale=(0.8, 0.8, 0.8), is_temp=True)
    data.box_count += 1

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text(f"Deliver 10 good quality products and discard bad ones. Use the quality scanner to analyze the boxes. Do not make mistakes.")

def level_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        data.correct / (10),
        f"Products delivered: {data.correct}/10"
    )

editor.specify_goal("deliver_products", f"Products delivered: {data.correct}/10", level_goal)

### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###

#TODO

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###

def on_toggle_handler(sender,simtime,is_on): 
    if is_on:
        TurnableConveyorBelt.first().set_target_speed(0)  # Stop when ON
        print("Conveyor belt brake switched to ON")
    else:
        TurnableConveyorBelt.first().set_target_speed(4)  # Move when OFF
        print("Conveyor belt brake switched to OFF")
    

def on_discard(trig:TriggerZone, gt:float, e:TriggerEvent):
    
    data.box_count -= 1
    
    if e.rfid_tag == ("Box_defected"):
        
        if SimEnvManager.first().get_sim_time() - data.last_sound_at > 5:
            editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(e.entity_name), color = Colors.Green)
            editor.play_sound(SpawnableSounds.ExplosionMagic, location = editor.get_location(e.entity_name))   
        editor.set_lifetime(e.entity_name, 0.01)
        data.last_sound_at = SimEnvManager.first().get_sim_time()
                
    else:
        
        if SimEnvManager.first().get_sim_time() - data.last_sound_at > 5:
            editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(e.entity_name), color = Colors.Red)
            editor.play_sound(SpawnableSounds.ExplosionPuff, location = editor.get_location(e.entity_name))
        editor.set_lifetime(e.entity_name, 0.01)
        editor.set_goal_state("deliver_products", GoalState.Fail, new_text="Failed: Invalid product discard")
        data.last_sound_at = SimEnvManager.first().get_sim_time()
        
def on_delivered(trig:DeliveryContainer, gt:float, e:TriggerEvent):
    data.box_count -= 1
    if e.rfid_tag == "Box_ok":
        data.correct += 1
    else:
        editor.set_goal_state("deliver_products",GoalState.Fail, new_text="Failed:Invalid delivery!")
    
    
def begin_play():
    print("begin play") 
    trigg = TriggerZone.first()
    trigg.on_triggered(on_discard)
    toggle = ToggleSwitch.first()
    toggle.on_toggle(on_toggle_handler)
    delivery_box = DeliveryContainer.first()
    delivery_box.on_delivered(on_delivered)
    on_reset()

editor.on_begin_play(begin_play)

### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("Level resetting")
    range_finder = RangeFinder.first()
    range_finder.editor_set_max_range(300)
    range_finder.editor_set_can_read_rfid_tags(True)
    ConveyorBelt.find("belt1").set_target_speed(5)
    ConveyorBelt.find("belt2").set_target_speed(5)
    data.reset()
    editor.set_goal_state("deliver_products", GoalState.Open)
    if ToggleSwitch.first().get_is_switched_on() == False:
        TurnableConveyorBelt.first().set_target_speed(4)

editor.on_level_reset(on_reset)

### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    
    if entity_name == "turn_button" and command == "Press":
        if data.current_rotation < 80:
            TurnableConveyorBelt.first().set_target_rotation(90)
            print("Set new rotation: 90")
            data.current_rotation = 90
        elif data.current_rotation >= 80:
            TurnableConveyorBelt.first().set_target_rotation(0)
            print("Set new rotation: 0")
            data.current_rotation = 0
    if entity_name == "discard_button" and command == "Press":
        if MovablePlatform.first().get_current_rotation()[0] < 5:
            MovablePlatform.first().set_target_location(0, 0.7, 1.5)
            MovablePlatform.first().set_target_rotation(45.0, 0.0, 0.0)
        else: 
            MovablePlatform.first().set_target_location(0, 0, 0)
            MovablePlatform.first().set_target_rotation(0.0, 0.0, 0.0)
    

        
editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    spawn_next()
    
    if data.box_count > 3:
        editor.set_goal_state("deliver_products",GoalState.Fail,"Failed: You jammed the delivery line!")

    
editor.on_tick(on_tick)
### END LEVEL TICK CODE ###
    

# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###

env = SimEnvManager.first()

while SimEnv.run_main():
    pass
