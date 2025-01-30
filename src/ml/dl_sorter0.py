### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

#spawn two different objects (A / B) with random orientation, scale and pos on belt and sort to left or right base din camera input.
#two other cameras that show A and B wih random orientation, scale and pos for training.

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
        self.last_spawn_at_train = -999999.0
        

data = DataModel()


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.SmallWarehouse)
editor.spawn_entity(SpawnableEntities.ConveyorBelt, "belt1", location=(0, 0, 0.1), rotation = (0,0,90))
editor.spawn_entity(SpawnableEntities.LargeConveyorBelt, "belt2", location=(6, 0, 0.1), rotation = (0,0,90))
editor.spawn_entity(SpawnableEntities.SmartCamera, "camera", location=(2.35, 0.0, 1.5), rotation=(0,0,180))
editor.spawn_static_mesh(SpawnableMeshes.Cube, material=SpawnableMaterials.SimpleColor, location=(2.35, 0.0, 0.75), scale=(0.5, .5, 1.5), color=Colors.Slategray)

editor.spawn_entity(SpawnableEntities.TriggerZone, "Barrel_Zone", location= (-0.05, -4.25, 0.75), scale=2)
editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, location=(-0.05, -4.25, 0.75))
editor.spawn_entity(SpawnableEntities.TriggerZone, "Cone_Zone", location=(-0.003, 4.21, 0.7), scale=2)
editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(-0.003, 4.21, 0.7), scale=2)

editor.spawn_entity(SpawnableEntities.ObjectSpawner, "spawner", location=(0, 0, 3.7), rotation=(0,0,-90))

editor.spawn_static_mesh(SpawnableMeshes.Plane,"plane1",  location=(-1, 0.0, 1.5), rotation=(0.0, 85.0, 180.0), scale=(2.0, 6, 1.0))
editor.spawn_static_mesh(SpawnableMeshes.Plane, "plane2", location=(1, 0.0, 1.5), rotation=(0, 85.0, 0), scale=(2.0, 6, 1.0))

def spawn_next():
    if SimEnvManager.first().get_sim_time() - data.last_spawn_at < 1.5:
        return
    data.last_spawn_at = SimEnvManager.first().get_sim_time()
    i = random.randint(0,1)
    if i == 0:
        editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, f"Barrel_{random.randint(0,999999)}", location=(0, 0, 2.0), rotation=Rotator3.random(), scale=random.uniform(0.8,1.2), simulate_physics=True, is_temp=True)
    elif i == 1:
        editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, f"Cone_{random.randint(0,999999)}", location=(0, 0, 2.0), rotation=Rotator3.random(), scale=random.uniform(1.8,2.2), simulate_physics=True, is_temp=True)

#training area
editor.spawn_entity(SpawnableEntities.SmartCamera, "camera_barrel", location=(5.8, -2.0, 5.5), rotation=(0,-90,0))
editor.spawn_entity(SpawnableEntities.SmartCamera, "camera_cone", location=(5.8, 2.0, 5.5), rotation=(0,-90,0))

def spawn_train():
    if SimEnvManager.first().get_sim_time() - data.last_spawn_at_train < 0.5:
        return
    data.last_spawn_at_train = SimEnvManager.first().get_sim_time()
    editor.spawn_static_mesh(SpawnableMeshes.BarrelGreen, location=(6, -2, 2.2), rotation=Rotator3.random(), scale=random.uniform(0.8,1.2), simulate_physics=True, is_temp=True, lifetime=0.5)  
    editor.spawn_static_mesh(SpawnableMeshes.TrafficCone, location=(6, 2, 2.2), rotation=Rotator3.random(), scale=random.uniform(1.8,2.2), simulate_physics=True, is_temp=True, lifetime=0.5)  
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def deliver_goal(goal_name: str):
    editor.set_goal_progress(goal_name, data.correct / 10.0, f"Deliver 10 items to their corresponding destinations. Incorrect devliveries count as -1. Delivered {data.correct}/10")
editor.specify_goal("deliver_goal", "Deliver 10 items to their corresponding destinations.", deliver_goal)

def acc_goal(goal_name: str):
    s = GoalState.Open
    if data.incorrect > 0:
        s = GoalState.Fail
    elif data.correct > 0:
        s = GoalState.Success
    editor.set_goal_state(goal_name, s)
editor.specify_goal("acc_goal", "Don't do any incorrect deliveries.", acc_goal, 0, True, True)

editor.set_goals_intro_text("You need to move Barrels and Cones to their correct destination. You have a camera to classify the objects using deep learning or computer vision. Note: Only the first item spawns automatically, after that you need to decide when to spawn in the next item using the ObjectSpawner.")
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
editor.add_hint(0,["How do I spawn the next object?", "Nothing is happening after the first object."], "You can manually spawn-in the next object to be delivered. For this simply call the 'spawn' method on the 'ObjectSpawner'.")
editor.add_hint(1,["Please show me some code to spawn-in the next object.", "How exactly do I spawn the next deliverable item?"], "[#4ABCA5](ObjectSpawner).[#DCDCAA](first)\(\).[#DCDCAA](spawn)\(\)")

editor.add_hint(3,["What is deep learning?", "How do I build a neural network?"], "To train a deep learning you will use the tinygrad framework. Start here to learn more, as there is a lot to cover: https://docs.tinygrad.org/mnist/")

editor.add_hint(5,["What are the other cameras for?", "Why are there barrels and cones constantly spawning and disappearing?"], "You can use the two other cameras to train a deep learning model. One camera always shows a cone, the other always a barrel. That way you can train a model learns to recognize if there is a cone or a barrel in the image.")
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
            data.correct -= 1
            if data.correct < 0:
                data.correct = 0
            col = Colors.Red
            print(f"Incorrect delivery of {a[0]} at {trig.entity_name}", col=Colors.Orange)
        editor.apply_impulse(e.entity_name, (0,0,20))
        editor.show_vfx(SpawnableVFX.ColorBurst, location = editor.get_location(e.entity_name), color = col)
        editor.play_sound(SpawnableSounds.ExplosionPuff, location = editor.get_location(e.entity_name))
        editor.set_lifetime(e.entity_name, 1.2)

        
        
        
def begin_play():
    for t in TriggerZone.find_all():
        t.on_triggered(on_deliver)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    editor.set_hidden("plane1", True)
    editor.set_hidden("plane2", True)
    data.reset()
    spawn_next()
    LargeConveyorBelt.find("belt2").set_target_speed(1.0)
    SmartCamera.find("camera_barrel").set_fov(20)
    SmartCamera.find("camera_cone").set_fov(20)
    SmartCamera.find("camera").set_fov(55)
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
def on_tick(simtime: float, deltatime: float):
    spawn_train()


editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#if you want to build a deep learning approach, unlock the "tinygrad" module and start here:
#https://docs.tinygrad.org/mnist/

env = SimEnvManager.first()

while SimEnv.run_main():
    #train a model to learn what cones and barrels look like:
    train_img_cone = SmartCamera.find("camera_cone").get_camera_frame()
    train_img_barrel = SmartCamera.find("camera_barrel").get_camera_frame()

    #predict if a cone or barrel is visible
    test_img_cone_or_barrel = SmartCamera.find("camera").get_camera_frame()
