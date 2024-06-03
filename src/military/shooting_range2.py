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
editor.spawn_entity(SpawnableEntities.MovablePlatform,"platform", location = (4.4, -13.95, 0.83+1),rotation=(0,0,90))
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(4.4, 6.0, 0.4), scale=(18,1,2.1), material=SpawnableMaterials.SimpleColorWorldAligned, color=Colors.Slategray)
#editor.spawn_static_mesh(SpawnableMeshes.Cube, "sdd", location = (4.4,6.3,2.5), scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Purple, simulate_physics=True, texture=SpawnableImages.TargetIndicator)
def spawn_target():
    for s in editor.get_all_spawns():
        if s.startswith("TargetRed") or s.startswith("TargetGreen"):
            editor.destroy(s)
            if s.startswith("TargetRed"):
                data.red_despawned.add(s)
        

    col = Colors.Red if random.random() > 0.2 else Colors.Green
    cols = str(col).replace("Colors.","")
    loc = (random.randint(4-8,4+8)+0.4,6.3,2.5)
    editor.spawn_static_mesh(SpawnableMeshes.Cube, "Target" + cols + str(random.randrange(0,99999)), location = loc, scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors(col), simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True)
    #editor.show_vfx(SpawnableVFX.)
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def on_bullet_hit(rifle:SniperRifle, gt:float, coll:CollisionEvent):
    if coll.entity_name in data.hits:
        return
    if coll.entity_name.startswith("TargetRed"):
        data.hit_red += 1
    elif coll.entity_name.startswith("TargetGreen"):
        data.hit_green += 1
        data.hit_red = 0 #reset on failure
    else:
        return
    data.hits.add(coll.entity_name)
    editor.destroy(coll.entity_name)
    editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(coll.entity_name), color = Colors.Red if coll.entity_name.startswith("TargetRed") else Colors.Green)
    editor.play_sound(SpawnableSounds.ExplosionPuff, location = editor.get_location(coll.entity_name))
    

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
    "Perfect accuracy: Take exactly 5 shots and hit 5 red targets. Don't miss any red targets.",
    acc_goal,
    0,
    True,
    True
)
### END GOAL CODE ###

editor.add_hint(0,["How do I aim at the targets?","I need help controlling the movable platform..."], """To aim at the targets that pop up randomly you need to rotate the movable platform. You can set the absolute rotation like this:
[#9CDCFE](platform) = [#4ABCA5](MovablePlatform).[#DCDCAA](first)\(\)
[#9CDCFE](yaw) = [#B5CEA8](45)
[#9CDCFE](platform).[#DCDCAA](set_target_rotation)\([#B5CEA8](0),[#B5CEA8](0),[#9CDCFE](yaw)\)
""")

editor.add_hint(1,["How to calculate to yaw angle between to rifle and the target?","Do I need to calculate the yaw angle between the rifle and the target?"],"Calculating the perfect aim-angle directly is quite involved. Instead I'd recommend trial and error to figure out what image distance corresponds to what aim angle or setting the aim-angle incrementally by aiming further left or further right until the target is in the middle of the image.")
editor.add_hint(2,["That! I wanna do that. But how do aim incrementally?"],"In your while loop get the image detections. Figure out a scaling factor for it. Add that to a yaw angle you initialized outside the loop and set the rotation accordingly.")
editor.add_hint(3,["Uhm yeah I'm gonna need to see some code for that aiming stuff..."],"""[#9CDCFE](yaw) = [#B5CEA8](0)
[#C586C0](while) [#4ABCA5](SimEnv).[#DCDCAA](run_main)\(\):
    [#9CDCFE](dects) = [#9CDCFE](rifle).[#DCDCAA](get_object_detections)\(\)
    [#C586C0](for) [#9CDCFE](d) [#C586C0](in) [#9CDCFE](dects):
        [#C586C0](if) [#9CDCFE](d).entity_name.[#DCDCAA](startswith)\([#CE9178]("TargetRed")\):
            [#9CDCFE](img_dist) = [#9CDCFE](d).img_left-[#B5CEA8](127)
            [#6A9955](#change current aim in direction of target)
            [#9CDCFE](yaw) += [#9CDCFE](img_dist)/[#B5CEA8](20.0)
            [#C586C0](if) [#9CDCFE](d).img_left > [#B5CEA8](124) [#C586C0](and) [#9CDCFE](d).img_left < [#B5CEA8](130):
                [#C586C0](break)
    [#9CDCFE](platform).[#DCDCAA](set_target_rotation)\([#B5CEA8](0),[#B5CEA8](0),[#9CDCFE](yaw)\)
""")

def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "Fire":
        data.shots_fired += 1
        data.last_shot_at = gametime

editor.on_player_command(on_player_command)


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    SniperRifle.first().on_bullet_hit(on_bullet_hit)
    on_reset()
    #cinematic()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    MovablePlatform.first().attach_entities()
    MovablePlatform.first().editor_set_location_limits((0,12,3))
    data.reset()



editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###

def on_tick(simtime: float, deltatime: float):
    if data.mytime > 9:
        data.mytime = 0.0
        spawn_target()
    else:
        data.mytime += deltatime


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


def cinematic():
    sleep(5)
    editor.play_camera_sequence([
        CameraWaypoint((4.4, -20.0, 0.8+1.4),[0,0,90],1),
        CameraWaypoint((4.4, -12, 0.8+1.3),[0,1,90],4)
    ])
    sleep(2)
    for i in range(18):
        col = Colors.Red if random.random() > 0.2 else Colors.Green
        cols = str(col).replace("Colors.","")
        loc = (4-8+0.4+i,6.3,2.5)
        editor.spawn_static_mesh(SpawnableMeshes.Cube, "Target" + cols + str(random.randrange(0,9999)), location = loc, scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors(col), simulate_physics=True, texture=SpawnableImages.TargetIndicator)
        sleep(0.3)


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###

