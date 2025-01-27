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
        self.correct = 0
        self.incorrect = 0
        self.seen:Set[str] = set()
        self.last_spawn_at = -999999.0
        

data = DataModel()


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.SmallWarehouse)
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt0", location=(-4.000,0.000,0.200)) #generated-code
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt1", location=(0, 0, 0.1), rotation = (0,0,90))
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt2", location=(1.8, -4.0, 0.0))
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt3", location=(1.8, 4.0, 0.0))
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt4", location=(5.8, 4.0, -0.1), rotation = (0,0,90))

editor.spawn_entity(SpawnableEntities.RangeFinder, "scan0", location=(2, 0, 0.5), rotation=(0,0,-90))
editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, location=(2, 0, 0), scale=(0.75, .75, 1), color=Colors.Slategray)
editor.spawn_entity(SpawnableEntities.RangeFinder, "scan1", location=(7.8, 3.45, 0.4),rotation=(0,0,-90))
editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, location=(7.8, 3.45, 0), scale=(0.75, .75, 0.8), color=Colors.Slategray)

editor.spawn_entity(SpawnableEntities.TriggerZone, "Barrel_Zone", location= (6.0, -4.0, 0.8), scale=2)
editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, location=(6.0, -4.0, 0.4))
editor.spawn_entity(SpawnableEntities.TriggerZone, "Box_Zone", location= (5.8, -0.25, 0.8), scale=2)
editor.spawn_static_mesh(SpawnableMeshes.CardboardBox, location=(5.8, -0.25, 0.3))
editor.spawn_entity(SpawnableEntities.TriggerZone, "Cone_Zone", location=(5.8, 8.2, 0.7), scale=2)
editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(5.8, 8.2, 0.2), scale=2)

editor.spawn_entity(SpawnableEntities.ObjectSpawner, "spawner", location=(-4, 0, 3.5), rotation=(0,0,-90))
def spawn_next():
    if SimEnvManager.first().get_sim_time() - data.last_spawn_at < 1.5:
        return
    data.last_spawn_at = SimEnvManager.first().get_sim_time()
    i = random.randint(0,2)
    if i == 0:
        editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, f"Barrel_{random.randint(0,999999)}", rfid_tag = "Barrel", location=(-4, 0, 1.5), simulate_physics=True, is_temp=True)
    elif i == 1:
        editor.spawn_static_mesh(SpawnableMeshes.CardboardBox, f"Box_{random.randint(0,999999)}", rfid_tag = "Box", location=(-4, 0, 1.5), simulate_physics=True, is_temp=True)
    elif i == 2:
        editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, f"Cone_{random.randint(0,999999)}", rfid_tag = "Cone", location=(-4, 0, 1.5), scale = 3, simulate_physics=True, is_temp=True)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def deliver_goal(goal_name: str):
    editor.set_goal_progress(goal_name, data.correct / 8.0, f"Deliver 8 items to their corresponding destinations. Delivered {data.correct}/8")
editor.specify_goal("deliver_goal", "Deliver 8 items to their corresponding destinations.", deliver_goal)

def acc_goal(goal_name: str):
    s = GoalState.Open
    if data.incorrect > 0:
        s = GoalState.Fail
    elif data.correct > 0:
        s = GoalState.Success
    editor.set_goal_state(goal_name, s)
editor.specify_goal("acc_goal", "Don't do any incorrect deliveries.", acc_goal, 0, True, True)

def time_goal(goal_name: str):
    if data.correct >= 10:
        return
    s = GoalState.Open
    t = max(0, 120 - SimEnvManager.first().get_sim_time())
    if t <= 0:
        s = GoalState.Fail
    elif data.correct > 0:
        s = GoalState.Success
    editor.set_goal_state(goal_name, s, f"Finish all deliveries in less than {t:.2f} seconds.")
editor.specify_goal("time_goal", "Finish all deliveries in less than 120 seconds.", time_goal, 0, True, True)
editor.set_goals_intro_text("You need to move items of 3 different categories along these conveyor belts to their correct destination. Only the first item spawns automatically, after that you need to decide when to spawn in the next item using the ObjectSpawner.")
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
editor.add_hint(0,["How do I spawn the next object?", "Nothing is happening after the first object."], "You can manually spawn-in the next object to be delivered. For this simply call the 'spawn' method on the 'ObjectSpawner'. Note: To beat the time limit, you'll need to spawn-in new objects before the delivery of the current one is completed.")
editor.add_hint(1,["Please show me some code to spawn-in the next object.", "How exactly do I spawn the next deliverable item?"], "[#4ABCA5](ObjectSpawner).[#DCDCAA](first)\(\).[#DCDCAA](spawn)\(\)")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_deliver(trig:TriggerZone, gt:float, e:TriggerEvent):
    a = e.entity_name.split("_")
    if a and a[0] in ("Box","Barrel","Cone") and e.entity_name not in data.seen:
        data.seen.add(e.entity_name)
        if trig.entity_name.startswith(a[0]):
            data.correct += 1
            col = Colors.Green
        else:
            data.incorrect += 1
            col = Colors.Red
            print(f"Incorrect delivery of {a[0]} at {trig.entity_name}", col=Colors.Orange)
        editor.apply_impulse(e.entity_name, (0,0,20))
        editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(e.entity_name), color = col)
        editor.play_sound(SpawnableSounds.ExplosionPuff, location = editor.get_location(e.entity_name))
        editor.set_lifetime(e.entity_name, 1.5)

        
        
        
def begin_play():
    print("begin play")
    for t in TriggerZone.find_all():
        t.on_triggered(on_deliver)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    for r in RangeFinder.find_all():
        r.editor_set_can_read_rfid_tags(True)
    data.reset()
    spawn_next()
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint((-5.000,0.000,-1),[0,-85,0],1),
    #     CameraWaypoint((-4.000,0.000,8.500),[0,-85,0],2),
    #     CameraWaypoint((0.000,0.000,8.500),[0,-85,0],1.7),
    #     #CameraWaypoint((0.000,0.000,8.500),[0,-85,90],1),
    #     #CameraWaypoint((0,4.000,8.500),[0,-85,90],2),
    #     CameraWaypoint((0,4.000,8.500),[0,-85,0],1.5),
    #     CameraWaypoint((5.800,4.000,8.500),[0,-85,0],1.3),
    #     #CameraWaypoint((5.800,4.000,8.500),[0,-85,-90],1),
    #     CameraWaypoint((5.800,-0.3,-1.2),[0,-70,-90],0.5)
    # ])


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    #print(f"{entity_type=}, {entity_name=}, {command=}")
    if entity_name == "spawner" and command == "Spawn":
        spawn_next()

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###

### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
