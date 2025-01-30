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
        self.target_id = random.randint(4,14)
        self.shots_fired = 0
        self.finished_at = -1.0
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.GrasslandOutdoor)
editor.spawn_entity(SpawnableEntities.SniperRifle, "rifle", location=(0,-3,0.2),rotation=(0,0,90))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"platform", location = (0,-3,0.2),rotation=(0,0,90))
#editor.spawn_static_mesh(SpawnableMeshes.Cube, "sdd", location = (4.4,6.3,2.5), scale = (0.5,.15,0.5), material = SpawnableMaterials.ColoredTexture, color = Colors.Purple, simulate_physics=True, texture=SpawnableImages.TargetIndicator)
def spawn_target():
    j = 0
    orig = Vector3(5,-3,0.51) - (0,-3,0.2)
    for i in range(20):
        #calc circle pos
        pos = orig.rotate_vector(Rotator3(0,0,j/20 * 360 + 90)) + (0,-3,0.2)
        j += 1
        col = Colors.Red if i == data.target_id else Colors.Green
        #editor.spawn_destructible("Target_" + str(i), color=col, location=pos)
        editor.spawn_static_mesh(SpawnableMeshes.Cube, "Target_" + str(i), location = pos, scale = 0.5, material = SpawnableMaterials.ColoredTexture, color = col, simulate_physics=True, texture=SpawnableImages.TargetIndicator, is_temp=True, weight=20.0)
    #editor.show_vfx(SpawnableVFX.)
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def on_bullet_hit(rifle:SniperRifle, gt:float, coll:CollisionEvent):
    print(coll.entity_name)
    if data.finished_at > 0:
        return
    if coll.entity_name == "Target_" + str(data.target_id):
        data.finished_at = gt
        #editor.destroy(coll.entity_name)
        pos = coll.impact_location
        editor.show_vfx(SpawnableVFX.ColorBurst, location = pos, color = Colors.Purple, scale=3)
        editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(coll.entity_name), color = Colors.Red, scale=1)
        editor.play_sound(SpawnableSounds.ExplosionPuff, location = pos)
        #editor.spawn_destructible(color=Colors.Red, location=pos)
        editor.spawn_static_mesh(SpawnableMeshes.Sphere, location = pos + (0,0,1), scale=(0.4,0.4,1.0), material=SpawnableMaterials.SimpleEmissive, color=Colors.Purple, is_temp=True, simulate_physics=True)
        if data.shots_fired == 1:
            editor.set_goal_state("acc_goal", GoalState.Success)
        sleep(0.6)
        editor.set_goal_state("hit_goal", GoalState.Success)
    

editor.set_goals_intro_text("The Easter Bunny was here! (Yes it was late... or early...)")

editor.specify_goal(
    "hit_goal",
    "Shoot the [red](red) box with the easter egg inside."
)

editor.specify_goal(
    "acc_goal",
    "Shoot only a single bullet",
    None,
    0,
    True,
    True
)
### END GOAL CODE ###

editor.add_hint(0,["How do I aim at the targets?","I need help controlling the movable platform..."], """The targets are distributed evenly along a circle around the platform. You can set the absolute rotation like this:
[#9CDCFE](platform) = [#4ABCA5](MovablePlatform).[#DCDCAA](first)\(\)
[#9CDCFE](yaw) = [#B5CEA8](45)
[#9CDCFE](platform).[#DCDCAA](set_target_rotation)\([#B5CEA8](0),[#B5CEA8](0),[#9CDCFE](yaw)\)
""")


def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "Fire":
        data.shots_fired += 1
        if data.shots_fired > 1:
            editor.set_goal_state("acc_goal", GoalState.Fail)

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
    MovablePlatform.first().editor_set_location_limits((0,0,0.01))
    MovablePlatform.first().editor_set_rotation_limits((0,0,360))
    data.reset()
    spawn_target()
    editor.set_goal_state("acc_goal", GoalState.Open, "Shoot only a single bullet.")
    editor.set_goal_state("hit_goal", GoalState.Open)



editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###

