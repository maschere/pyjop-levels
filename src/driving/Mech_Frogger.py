### INIT CODE - DO NOT CHANGE ###
from pyjop import *
import numpy as np
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
        self.last_car_spawn = -999

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.Bridge)

editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(2.8, 8, 0), scale=(3, 3, 3))
editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(3, 7, 0), scale=(3, 3, 3))
editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(-2, -8, 0), scale=(3, 3, 3))
editor.spawn_static_mesh(SpawnableMeshes.SmallFence, location=(-2, 8, 0), rotation=(0, 0, 90))
editor.spawn_static_mesh(SpawnableMeshes.SmallFence, location=(5.2, 7, 0), rotation=(0, 0, 0), scale=(1.5, 1, 1))
editor.spawn_static_mesh(SpawnableMeshes.SmallFence, location=(0, -7.5, 0), rotation=(0, 0, 0), scale=(1.5, 1, 1))
editor.spawn_static_mesh(SpawnableMeshes.SmallFence, location=(3.2, -7.5, 0), rotation=(0, 0, 0), scale=(1.5, 1, 1))

editor.spawn_entity(SpawnableEntities.ProximitySensor, "proximity_sensor1", location=(30, -8, 0))
editor.spawn_entity(SpawnableEntities.RangeFinder, "range_finder1", location=(-30, 8, 0))

editor.spawn_entity(SpawnableEntities.TriggerZone, "goal_zone", location=(8, -8, 0), scale=(2, 2, 0.5))	
editor.spawn_entity(SpawnableEntities.HumanoidRobot, "bot1", location=(0,8,0))

def spawn_car():
    spawn_interval = random.uniform(1.5, 2.5)
    if SimEnvManager.first().get_sim_time() - data.last_car_spawn < spawn_interval:
        return
    
    id = random.randint(2, 999999)
    car_positions = [
    ((40, -5.5, 0), (0, 0, 180)),  # Lane 1, direction 1
    ((40, -2, 0), (0, 0, 180)),    # Lane 2, direction 1
    ((-40, 5, 0), (0, 0, 0)),     # Lane 3, direction 2
    ((-40, 2, 0), (0, 0, 0))      # Lane 4, direction 2
    ] 
    car_start_pos, car_rotation = random.choice(car_positions)
        
    # spawn car and weld a trigger zone to the car to check collisions
    editor.spawn_entity(SpawnableEntities.SimplePhysicsCar, f"car_{id}", location=(car_start_pos), rotation=(car_rotation), is_temp=True)
    editor.spawn_entity(SpawnableEntities.TriggerZone, f"trigger_{id}", location=(car_start_pos), scale=(6,2,3), is_temp=True)
    sleep()
    child = f"trigger_{id}"
    parent= f"car_{id}"
    editor.set_hidden(f"trigger_{id}", is_hidden=True)
    editor.weld_entities(child, parent)                   
    SimplePhysicsCar.find(f"car_{id}").apply_impulse(15)
    data.last_car_spawn = SimEnvManager.first().get_sim_time()
    


def on_collision(handler:TriggerZone,gt:float,e:TriggerEvent):
    if e.entity_name == "bot1":
        print("Robot hit by a car!")
        editor.show_vfx(SpawnableVFX.Explosion, location = editor.get_location(e.entity_name))
        editor.play_sound(SpawnableSounds.Explosion)
        editor.destroy("bot1")
        editor.set_goal_state("level_goal", GoalState.Fail, new_text="Failed: Robot was hit by a car!")

        
def bot_in_zone(handler:TriggerZone, gt:float, e:TriggerEvent):
    if e.entity_name == "bot1":
        print("Robot entered the target zone!")
        editor.set_goal_state("level_goal", GoalState.Success)
        
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Dangerous crossing")

def crossing_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        0 / 1,
        f"Cross the road and reach the target zone without getting hit by a car",
    )

editor.specify_goal("level_goal", "Cross the road and reach the target zone without getting hit by a car", crossing_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")	
    TriggerZone.find("goal_zone").on_triggered(bot_in_zone)
    on_reset()

    
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    ProximitySensor.first().editor_set_max_range(20)
    RangeFinder.first().editor_set_max_range(700)
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    
    if entity_name == "bot1" and command == "setWalking":
        print("Player set walking!")
        array_data = val.array_data
        speed = float(array_data[0][1])
        print(f"player set speed: {speed}")
        if speed > 0.2: HumanoidRobot.first().set_walking(float(array_data[0][0]), 0.3)
        
editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    spawn_car()
    spawns = editor.get_all_spawns()
    for spawn in spawns:
        loc = editor.get_location(spawn)
        if loc[0] > 40 or loc[0] < -40:
            editor.destroy(spawn)
    trigger_zones = TriggerZone.find_all()
    for trigger_zone in trigger_zones:
        if trigger_zone.entity_name != "goal_zone":
            trigger_zone.on_triggered(on_collision)
    
    sleep()
    
editor.on_tick(on_tick)
### END LEVEL TICK CODE ###
 

# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###


env = SimEnvManager.first()
bot = HumanoidRobot.first()

while SimEnv.run_main():
    pass
