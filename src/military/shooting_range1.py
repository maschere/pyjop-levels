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
editor.spawn_entity(SpawnableEntities.SniperRifle, "rifle", location=(4.4, -15.95, 0.8+1.3),rotation=(0,0,90))
editor.spawn_entity(SpawnableEntities.LargeConveyorBelt,"conveyor", location = (4.4, 4.0, 0.8), is_controllable=False)
editor.spawn_static_mesh(SpawnableMeshes.Cube, location=(4.4, 4.0, 0.4), scale=(12,2,0.8), material=SpawnableMaterials.SimpleColorWorldAligned, color=Colors.Slategray)
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def on_bullet_hit(rifle:SniperRifle, gt:float, coll:CollisionEvent):
    if coll.entity_name in data.hits:
        return
    if coll.entity_name.startswith("TargetRed"):
        data.hit_red += 1
    elif coll.entity_name.startswith("TargetGreen"):
        data.hit_green += 1
        data.hit_red = 0 #reset of failure
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
    "Perfect accuracy: Take exactly 5 shots. Hit 5 red targets. Don't hit any green targets. Don't miss any red targets.",
    acc_goal,
    0,
    True,
    True
)
### END GOAL CODE ###

editor.add_hint(0,["How does the rifle scope work?","Do I need image processing to work with the rifle?"], "The sniper rifle is equipped with a scope that has an integrated YOLO-like image detection module. It can accurately draw bounding boxes around any objects visible in the scopes viewport. An additional laser range scanner measures the real distance to the target and scans its real size.")

editor.add_hint(2,["How do pull the trigger and fire the sniper rifle?"], "With the fire command:\n[#4ABCA5](SniperRifle).[#DCDCAA](first)\(\).[#DCDCAA](fire)\(\)")

editor.add_hint(4,["The bullet seems to drop.", "Is the bullet affected by gravity?", "How are the ballistics modelled?"], "The bullet uses a realistic G7 drag model for 7.62x51mm ammo. As such it takes gravity, wind, temperature and humidity into account. It also interacts with various surface materials to calculate impact engergy, penetration and recoil.")

editor.add_hint(6,["My rifle shots always lag behind the target.", "I keep missing the target with my shots."], "Increasing the tick-rate (see the Perks menu) greatly improves accuracy for this environment. However it also works with the default tick-rate of 2Hz. Fire slightly before the target reaches the middle of the scope's image.")
editor.add_hint(7,["Please provide an example for zeroing in on the red targets."], """[#C586C0](while) [#4ABCA5](SimEnv).[#DCDCAA](run_main)\(\):
    [#6A9955](#get yolo detections)
    [#9CDCFE](detects) = [#9CDCFE](rifle).[#DCDCAA](get_object_detections)\(\)
    [#6A9955](#get raw image for debugging)
    [#9CDCFE](img) = [#9CDCFE](rifle).[#DCDCAA](get_camera_frame)\(\)
    [#C586C0](for) [#9CDCFE](d) [#C586C0](in) [#9CDCFE](detects):
        [#C586C0](if) [#9CDCFE](d).entity_name.[#DCDCAA](startswith)\([#CE9178]("TargetRed")\):
            [#6A9955](#color bounding box in red)
            [#9CDCFE](img)[[#9CDCFE](d).img_top : [#9CDCFE](d).img_top+[#9CDCFE](d).img_height, [#9CDCFE](d).img_left : [#9CDCFE](d).img_left+[#9CDCFE](d).img_width, [#B5CEA8](0)] = [#B5CEA8](255)
            [#DCDCAA](print)\([#9CDCFE](d).img_left\)
            [#DCDCAA](print)\([#9CDCFE](img)\) [#6A9955](#debug print)
            [#6A9955](#decide on d.img_left threshold to fire)
            [#C586C0](break)
""")
editor.add_hint(8,["What's a good threshold to fire at?","How do I prevent shooting the same target multiple times?","How do I stop shooting at targets that have fallen off?"], """Try shooting the the target when it is between 105 and 135 pixels from the left edge. To prevent misfires also take the y coordinate into account and only shoot if the top edge of the bounding box is below 135. In code:
[#C586C0](if) [#9CDCFE](d).img_top<[#B5CEA8](135) [#C586C0](and) [#9CDCFE](d).img_left > [#B5CEA8](105) [#C586C0](and) [#9CDCFE](d).img_left < [#B5CEA8](135):
    [#9CDCFE](rifle).[#DCDCAA](fire)\(\)
    [#DCDCAA](sleep)\([#B5CEA8](1.5)\)
    [#C586C0](break)
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
    editor.ping((0,0,0),target_entity="rifle")
    # sleep(5)
    # editor.play_camera_sequence([
    #     CameraWaypoint((4.4, -20.0, 0.8+1.5),[0,0,90],3),
    #     CameraWaypoint((4.4, 5, 0.8+1.3),[0,1,90],1)
    # ])


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    LargeConveyorBelt.first().set_target_speed(-3)
    data.reset()



editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
def on_tick(simtime: float, deltatime: float):
    spawns = editor.get_all_spawns()
    for s in spawns:
        if s.startswith("TargetRed") or s.startswith("TargetGreen"):
            loc = editor.get_location(s)
            if loc.z < 1.0 or loc.x > 10 or loc.x < -3 or loc.y > 5:
                editor.destroy(s)
                # if s in data.hits:
                #     data.hits.remove(s)
                if s.startswith("TargetRed"):
                    data.red_despawned.add(s)
                sleep()
    if data.mytime > 7:
        data.mytime = 0.0

        if random.random() > 0.2:
            editor.spawn_static_mesh(SpawnableMeshes.Cube, f"TargetRed" + str(random.randrange(0,99999)), location = (9, 4.3, 2.7), scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Red, simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True)
        else:
            editor.spawn_static_mesh(SpawnableMeshes.Cube, f"TargetGreen" + str(random.randrange(0,99999)), location = (9, 4.3, 2.7), scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Green, simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True)
    else:
        data.mytime += deltatime


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
