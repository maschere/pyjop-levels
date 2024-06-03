### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.hit_red = 0
        self.hit_green = 0
        self.red_despawned:Set[str] = set()
        self.shots_fired = 0
        self.hits:Set[str] = set()
        self.mytime = 0.0
        self.last_shot_at = -1.0
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.MilitaryBase)
editor.spawn_entity(SpawnableEntities.SniperRifle, "rifle", location=(4.4, -13.95, 0.8+1),rotation=(0,0,90))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"platform", location = (4.4, -13.95, 0.8+1),rotation=(0,0,90))
editor.spawn_entity(SpawnableEntities.LaunchPad,"pad", location = (4.4,6.3,0.5))
editor.spawn_static_mesh(SpawnableMeshes.Plane, location = (4.4,5.1,1.4), material=SpawnableMaterials.Glass, scale = 3,rotation=(0,89,90))

def spawn_target():
    spawns = editor.get_all_spawns()
    for s in spawns:
        if s.startswith("TargetRed"):
            if editor.get_location(s).z < 1.7:
                editor.destroy(s)
                data.red_despawned.add(s)
                sleep()
    editor.set_rotation("pad",(0,0,(random.uniform(80,100) * random.choice([-1,1]))-90))
    sleep()
    editor.spawn_static_mesh(SpawnableMeshes.Cube, "TargetRed" + str(random.randrange(0,99999)), location = (4.4,6.3,0.9), scale = (0.5,.5,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Red, simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True)

    #editor.apply_impulse()
    sleep()
    sleep()
    LaunchPad.first().launch(random.uniform(0.8,0.9))
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
    editor.destroy(coll.entity_name)
    editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(coll.entity_name), color = (10,0.1,0.3))
    editor.play_sound(SpawnableSounds.Explosion, location = editor.get_location(coll.entity_name))

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
    "Perfect accuracy: Take exactly 5 shots. Hit 5 targets. Don't miss any targets.",
    acc_goal,
    0,
    True,
    True
)
### END GOAL CODE ###

editor.add_hint(0,["This challenge seems really hard. Where do I even begin?"], "It's highly recommended to solve the other shooting arena levels before attempting this one. Here, you'll need to figure out pitch and yaw angles based on the image detections the scope gives you.")


def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "Fire":
        data.shots_fired += 1
        data.last_shot_at = gametime

editor.on_player_command(on_player_command)


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    SniperRifle.first().on_bullet_hit(on_bullet_hit)
    #editor.set_clickable("pad",False)
    on_reset()
    # sleep(3.3)
    # random.seed(1)
    # editor.play_camera_sequence([
    #     CameraWaypoint((4.4, -20.0, 0.8+1.5),[0,0,90],0.5),
    #     CameraWaypoint((4.4, -18.0, 0.8+1.5),[0,1,90],1.8),
    #     CameraWaypoint((4.4, -10, 0.8+2.5),[0,35,120],0.4),
    #     CameraWaypoint((4.4, -8, 0.8+3.0),[0,10,130],0.4),
    #     CameraWaypoint((4.4, -7, 0.8+2.5),[0,-5,135],0.4),
    #     CameraWaypoint((4.4, -7, 0.8+2.5),[0,-8,137],0.8)
    # ])


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    MovablePlatform.first().attach_entities()
    MovablePlatform.first().editor_set_location_limits([1,5,3])
    MovablePlatform.first().editor_set_rotation_limits([80,80,180])
    data.reset()



editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###

def on_tick(simtime: float, deltatime: float):
    spawns = editor.get_all_spawns()
    for s in spawns:
        if s.startswith("TargetRed") and s not in data.red_despawned:
            loc = editor.get_location(s)
            dist = (loc - (4.4,6.3,0.9)).length
            if dist > 3 and loc.z < 1.7:
                editor.destroy(s)
                data.red_despawned.add(s)
                sleep()
    if data.mytime > 10:
        data.mytime = 0.0
        spawn_target()
    else:
        data.mytime += deltatime


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
