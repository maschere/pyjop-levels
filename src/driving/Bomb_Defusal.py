### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import math
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.time_counter = 0.0
        self.distance_to_bomb = 9999
        self.bomb_site = random.choice( [(-11.3, 1.85, 0.0) , (4.5,0.0,0.0), (-1.00,-12.300,0.000)] ) #three different coordinates for bomb location
        self.bomb_defused = 0
        self.bomb_timer = 90
        self.start_loc_x = random.randint(-4, 4)
        self.start_loc_y = random.randint(5, 9)
        
data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)

editor.spawn_static_mesh(SpawnableMeshes.Door, "door", material=SpawnableMaterials.SimpleColor, color=(Colors.Silver), location=(0.550,10.500,0.000), scale=(1.388, 1.0, 1.304)) #generated-code

editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary1", material=SpawnableMaterials.SimpleColor, color=(Colors.Slategrey), location=(-5.000,-14.700,0.000), scale=(20.000,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary2", material=SpawnableMaterials.SimpleColor, color=(Colors.Slategrey), location=(10.200,-14.700,0.000), scale=(10.363,0.187,7.019)) #generated-code #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary3", material=SpawnableMaterials.SimpleColor, color=(Colors.Slategrey), location=(15.300,-4.650,0.000), rotation=(0.000,0.000,90.000), scale=(20.000,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary4",material=SpawnableMaterials.SimpleColor,  color=(Colors.Slategrey), location=(-14.900,-4.650,0.000), rotation=(0.000,0.000,90.000), scale=(20.000,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary5", material=SpawnableMaterials.SimpleColor, color=(Colors.Slategrey), location=(-14.900,7.900,0.000), rotation=(0.000,0.000,90.000), scale=(5.071,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary6", material=SpawnableMaterials.SimpleColor, color=(Colors.Slategrey), location=(15.300,7.900,0.000), rotation=(0.000,0.000,90.000), scale=(5.071,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary7",material=SpawnableMaterials.SimpleColor,  color=(Colors.Slategrey), location=(-4.850,10.350,0.000), scale=(20.000,0.187,7.019)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.Cube, "boundary8",material=SpawnableMaterials.SimpleColor,  color=(Colors.Slategrey), location=(10.150,10.350,0.000), scale=(10.039,0.187,7.019)) #generated-code

#back wall
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(-8.0, -10.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(-4.0, -10.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(0.0, -10.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(4.0, -10.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(8.0, -10.0, 0.0))

# verticals 1
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(4, -10.0, 0.0), rotation=(0.0, 0.0, 90.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(4, -1.0, 0.0), rotation=(0.0, 0.0, 90.0))

editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(-4, -10.0, 0.0), rotation=(0.0, 0.0, 90.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(-4, -1.0, 0.0), rotation=(0.0, 0.0, 90.0))

# front walls
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(-8.0, 3.0, 0.0))
 #generated-code
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(4.0, 3.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", location=(4.0, -1.0, 0.0))
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", color=(1.0000,1.0000,1.0000), location=(-14.600,3.000,0.000), scale=(1.665,1.000,1.000)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", color=(1.0000,1.0000,1.0000), location=(8.050,3.000,0.000), scale=(1.761,1.000,1.000)) #generated-code
editor.spawn_static_mesh(SpawnableMeshes.FenceLarge, f"fence_{random.randint(0,999999)}", color=(1.0000,1.0000,1.0000), location=(-9.600,-1.050,0.000), rotation=(0.000,0.000,90.000)) #generated-code

#lower left barrels
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel1", color=(1.0000,1.0000,1.0000), location=(-10.250,2.000,0.000)) 
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel2", color=(1.0000,1.0000,1.0000), location=(-12.250,2.500,0.000))
editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, "barrel3", color=(1.0000,1.0000,1.0000), location=(-12.250,1.8,0.000)) 

# lower right barrels
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel4", color=(1.0000,1.0000,1.0000), location=(4.30,2.000,0.000)) 
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel5", color=(1.0000,1.0000,1.0000), location=(5.00,1.500,0.000)) 

# top barrels 
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel6", color=(1.0000,1.0000,1.0000), location=(-1.30,-11.000,0.000)) 
editor.spawn_static_mesh(SpawnableMeshes.BarrelRed, "barrel7", color=(1.0000,1.0000,1.0000), location=(-1.00,-11.500,0.000))


# others
editor.spawn_entity(SpawnableEntities.ServiceDrone, "drone", location=(data.start_loc_x , data.start_loc_y, 0), rotation=(0,0,180))
editor.spawn_entity(SpawnableEntities.SmartTracker, "gps", location=(data.start_loc_x, data.start_loc_y ,2.5))
editor.spawn_entity(SpawnableEntities.DataExchange, "data_exch", location=(4.85, 12.75, 0.0)) #generated-code
editor.spawn_entity(SpawnableEntities.RemoteExplosive, "bomb", location=(data.bomb_site), is_temp=True)



### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Use the bomb disposal robot to find and defuse the bomb before the time runs out! You can get the location of the bomb from the intelligence center")

def defuse_bomb(goal_name: str):
    if RemoteExplosive.first() == None: # bomb has exploded and despawned
        editor.set_goal_state(goal_name, GoalState.Fail)
    else:
        editor.set_goal_progress(
        goal_name,
        data.bomb_defused,
        f"Distance to bomb: {data.distance_to_bomb:.2f}\n Time until detonation: {RemoteExplosive.first().get_countdown():.2f}"
    )

editor.specify_goal("defuse_bomb_goal", "Stop near the bomb to defuse it!", defuse_bomb)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")    
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("Level resetting")
    data.reset()
    editor.weld_entities("gps","drone")
    editor.set_location("drone", (data.start_loc_x, data.start_loc_y))
    editor.spawn_entity(SpawnableEntities.RemoteExplosive, "bomb", location=(data.bomb_site), is_temp=True)
    sleep(1) # this seems to be necessary for the env to register that the bomb exists after previous spawn code
    RemoteExplosive.first().set_countdown(data.bomb_timer)
    DataExchange.first().set_data("bomb_location", data.bomb_site)
    editor.set_goal_state("defuse_bomb_goal", GoalState.Open)
    


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    pass

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    
    drone_location = editor.get_location("drone")
    bomb_location = editor.get_location("bomb")

    # Extract coordinates
    drone_x, drone_y = drone_location.xy[:2]
    bomb_x, bomb_y = bomb_location.xy[:2]

    distance = math.sqrt((drone_x - bomb_x)**2 + (drone_y - bomb_y)**2)
    data.distance_to_bomb = distance
    threshold_distance = 1.5
    if distance < threshold_distance:
        data.bomb_defused = 1

        
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
