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
        self.hit_red = 0
        self.red_despawned:Set[str] = set()
        self.shots_fired = 0
        self.hits:Set[str] = set()
        self.mytime = 0.0
        self.last_shot_at = -1.0
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.MilitaryBase)
editor.spawn_entity(SpawnableEntities.SniperRifle, "rifle", location=(4.4, -15.95, 0.8+1.3),rotation=(0,0,90))
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(4.4, 4.0, 0.8), scale=(6,2,2), material=SpawnableMaterials.SimpleColorWorldAligned, color=Colors.Slategray)
#editor.spawn_entity(SpawnableEntities.TriggerZone, "trigger", location=(4.4, 4.0, 1.8), scale=(6,2,0.2))
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def on_bullet_hit(rifle:SniperRifle, gt:float, coll:CollisionEvent):
    if coll.entity_name in data.hits:
        return
    if coll.entity_name.startswith("TargetRed"):
        data.hit_red += 1
    else:
        return
    data.hits.add(coll.entity_name)

def hit_goal(goal_name:str):
    prog = data.hit_red / 5.0
    editor.set_goal_progress(goal_name, prog, f"Hit 5 [red](red) targets. {data.hit_red}/5")

editor.specify_goal(
    "hit_goal",
    "Hit 5 [red](red) targets.",
    hit_goal,
    1,
    True,
    False
)

def acc_goal(goal_name:str):
    if data.hit_red >= 5:
        return
    s = GoalState.Success
    fired = data.shots_fired
    if SimEnvManager.first().get_sim_time() < data.last_shot_at + 0.7:
        fired -= 1
    more_fired = fired > data.hit_red
    
    if data.shots_fired > 5 or more_fired or len(data.red_despawned) > data.hit_red:
        s = GoalState.Fail
    elif data.shots_fired == 0:
        s = GoalState.Open
    editor.set_goal_state(goal_name, s)

editor.specify_goal(
    "acc_goal",
    "Perfect accuracy: Take exactly 5 shots. Hit 5 red targets. Don't miss any red targets.",
    acc_goal,
    0,
    True,
    True
)
### END GOAL CODE ###

editor.add_hint(0,["How does the rifle scope work?","Do I need image processing to work with the rifle?"], "The sniper rifle is equipped with a scope that has an integrated YOLO-like image detection module. So you do not need to process any pixel data, you already get the full detections. Mening you trigger the shot, if a TargetRed is detected. Alternatively simple time-interval based shooting is also possible here.")

editor.add_hint(2,["How do pull the trigger and fire the sniper rifle?"], "With the fire command:\n[#4ABCA5](SniperRifle).[#DCDCAA](first)\(\).[#DCDCAA](fire)\(\)")

editor.add_hint(4,["The bullet seems to drop.", "Is the bullet affected by gravity?", "How are the ballistics modelled?"], "The bullet uses a realistic G7 drag model for 7.62x51mm ammo. As such it takes gravity, wind, temperature and humidity into account. It also interacts with various surface materials to calculate impact engergy, penetration and recoil. For this level the muzzle velocity is reduced though.")


def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "Fire":
        data.last_shot_at = gametime
        data.shots_fired += 1

editor.on_player_command(on_player_command)


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    SniperRifle.first().on_bullet_hit(on_bullet_hit)
    on_reset()
    editor.ping(target_entity="rifle")
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint((4.4, -20.0, 0.8+1.5),[0,0,90],3),
    #     CameraWaypoint((4.4, 5, 0.8+1.3),[0,1,90],1)
    # ])


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()



editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    if simtime < 1:
        return
    spawns = editor.get_all_spawns()
    for s in spawns:
        if s.startswith("TargetRed") and s not in data.red_despawned:
            loc = editor.get_location(s)
            if loc.z < 1.3 or loc.y > 5:
                editor.destroy(s)
                data.red_despawned.add(s)
                sleep()
    if data.mytime > 7:
        data.mytime = 0.0

        editor.spawn_static_mesh(SpawnableMeshes.Cube, f"TargetRed" + str(random.randrange(0,99999)), location = (4.4, 4.3, 2.7), scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Red, simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True)
    else:
        data.mytime += deltatime


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
