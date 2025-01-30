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
        self.target_loc = Vector3(random.uniform(5,35),random.uniform(-20,20),random.uniform(2,4))
        self.points = 0
        self.shots_fired = 0
        self.hit_at = -10.0

    def move_target(self):
        self.target_loc = Vector3(random.uniform(5,35),random.uniform(-20,20),random.uniform(2,4))
        #travel_dist = (editor.get_location("target_area") - self.target_loc).length
        editor.set_location("target_area", self.target_loc + (-5,5,0), 1)
        editor.set_location("target_center_1m_above", self.target_loc + (0,0,1), 1)
        #print("Changing target location...")
        
        
TARGET_POINTS = 200
MAX_SHOTS = 3
data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.GrasslandOutdoor)
editor.set_map_bounds(extends=(92,92,16))
editor.spawn_entity(SpawnableEntities.Artillery, "artillery", location=(-25, 0, 0))
editor.spawn_entity(SpawnableEntities.SmartWall, "target_area", rotation=(-90,0,0), scale=(10,1,10))
editor.spawn_entity(SpawnableEntities.GPSWaypoint, "target_center_1m_above")
editor.spawn_entity(SpawnableEntities.GPSWaypoint, "origin", location=(-25, 0, 3))

### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("You have to calibrate this artillery gun. You receive 1 to 100 points for each hit, depending on distance to the center of the target area. Reach at least [*bold](200 points) and try to use no more than [*bold](3 shells).")
def goal_up(goal_name: str):
    s = GoalState.Open
    if data.shots_fired <= 0:
        pass
    elif data.shots_fired <=3:
        s = GoalState.Success
    else:
        s = GoalState.Fail
    editor.set_goal_state("accGoal", s, f"{data.shots_fired} / {MAX_SHOTS} shells fired.")
    editor.set_goal_progress("pointGoal", data.points / TARGET_POINTS, f"{data.points} / {TARGET_POINTS} points reached." )

editor.specify_goal("pointGoal", f"{data.points} / {TARGET_POINTS} points reached...",goal_up)
editor.specify_goal("accGoal", f"{data.shots_fired} / {MAX_SHOTS} shells fired...", goal_value=0, is_optional=True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How can I calculate the yaw angle / orientation towards the target?"], "You can figure out the math by looking at the problem from above. Draw the resulting triangle and you'll see how to calculate the required angle. Also the included Vector3 class has a function [*bold](find_lookat_rotation) which could help you...")

editor.add_hint(2,["How can I estimate the power needed?"], "This one is a little tricky. The shell will receive an impulse once it is fired and then fly a parabola arc until it hits a target. A nice explaination can the found here: https://www.omnicalculator.com/physics/projectile-motion")

editor.add_hint(4,["Is there a helper function to draw the projectile path?"], "Yes. Check the method [*bold](draw_throw_prediction) in the SimEnvManager class.")
### END HINTS ###

### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###

def on_coll(w: SmartWall, gt: float, col: CollisionEvent):
    if col.entity_type != "ArtilleryBullet":
        return
    if col.at_time < data.hit_at + 1:
        return
    data.hit_at = col.at_time
    dist = (col.impact_location.xy - data.target_loc.xy).length
    
    dist2 = dist*dist
    points = clamp(90 - dist2*5,1,90)
    if dist < 0.5:
        points = 100
        print(f"BULLSEYE! Target hit {dist:.2f}m from center.", col=Colors.Orange)
    else:
        print(f"Target hit {dist:.2f}m from center.")
    data.points += int(points)
    print(f"+{points}", col=Colors.Green)
    data.move_target()

def begin_play():
    target = SmartWall.first()
    target.on_collision(on_coll)
    #editor.set_collision_enabled("target_center",False)
    on_reset()
    #print("Please make sure you have updated the game to the most recent version v0.5.6 before playing this level!", col=Colors.Orange)


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    SmartWall.first().editor_set_can_read_local_coll(True)
    SmartWall.first().editor_set_can_read_world_coll(True)
    data.reset()
    data.move_target()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if entity_name == "artillery" and command == "Fire":
        data.shots_fired += 1

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###



# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#this template code will be provided to the player
#add level specific hints or boilerplate code here.

arty = Artillery.first()

env = SimEnvManager.first()
env.reset()

#aim artillery
arty.set_target_rotation(0,45,-10)
sleep(5)


while SimEnv.run_main():
    # fire the artillery
    arty.fire(20) #fire projectile with 20 m/s velocity
    sleep(3)