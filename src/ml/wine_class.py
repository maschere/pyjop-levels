### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import pandas as pd
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.num_correct = 0
        self.num_incorrect = 0
        self.current_label = ""
        self.handled_wines:set[str] = set()
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.WineCellar)
editor.spawn_entity(SpawnableEntities.RangeFinder,"FeatureExtractor",location = (-0.05, -7, 0.4), rotation = (0,0,180))
editor.spawn_static_mesh(SpawnableMeshes.Cube,location = (-0.05, -7, 0), scale=(0.5,0.5,0.8), material=SpawnableMaterials.SimpleColorWorldAligned, color=0.05)
editor.spawn_entity(SpawnableEntities.TurnableConveyorBelt,"turnbelt",location = (0,-3,0))
editor.spawn_entity(SpawnableEntities.DataExchange, "Database", location=(0, 3, 0))
editor.spawn_entity(SpawnableEntities.ObjectSpawner, "spawner", location=(-0.0, -2.9, 2.95), rotation = (0,0,180))

for p in [("good",(2.2,-3,0)), ("bad",(-2.2,-3,0)), ("ok",(0,-0.8,0))]:
    editor.spawn_entity(SpawnableEntities.TriggerZone, p[0], p[1], scale = (1.4,1.9,1.6), rotation=0 if p[0]!="ok" else (0,0,90))
    editor.spawn_static_mesh(SpawnableMeshes.WoodenBox, location=p[1], scale = (7.5,5,3), rotation=0 if p[0]!="ok" else (0,0,90))
    #editor.spawn_entity(SpawnableEntities.InputBox,f"{p[0]}_box")
    #editor.set_hidden(p[0], True)
sleep(0.5)


f = editor.get_dataset_file(CsvDatasets.winequality)
wine = pd.read_csv(f).sample(frac=1, ignore_index=True, random_state=42)
N = 10
def spawn_next_bottle():
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it makes sense to call this function on each level reset to respawn the temp objects in their original location.
    idx = random.randint(5500,6496)
    x = wine.loc[idx, wine.columns != "label"].to_dict()
    y = str(wine.loc[idx, ["label"]].item().lower())
    mesh = SpawnableMeshes.Bottle1 #ok
    if y == "good":
        mesh = SpawnableMeshes.Bottle2
    elif y == "bad":
        mesh = SpawnableMeshes.Bottle3
    data.current_label = y
    n = random.randint(0,9999999)
    editor.spawn_static_mesh(mesh, f"wine{n}", location=(0.35,-3,1.5), rotation=(0,90,0), is_temp=True, simulate_physics=True, scale=2.5)
    sleep(0.5)
    editor.set_feature_data(f"wine{n}", x , y)

        
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("In the DataExchange there is a dataset with 12 chemical measurements of 5500 different wines. Professional someliers rated these wines as either 'good', 'ok' or 'bad'. We have some new wines coming in, but we cannot pay the someliers anymore. So you will need to use machine learning to predict the rating the someliers would have given these new wines!")
editor.specify_goal("sort_goal", f"Correctly classify and sort at least {N} wine bottles into their corresponding crates.", None, 1, hide_next=False)
editor.specify_goal("acc_goal", "Classify at most 3 bottles incorrectly.", None, 0, is_optional=True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How can I determine how good a wine is? I'm NOT a somelier! Hell, I don't even know what a somlier is!!"], "The range finder is equipped with a feature extractor, that can extract certain measurements for each wine you point it at. Based on the reference dataset in the DataExchange, you can compute a statistical learning model that should be able to classify the wines correctly most of the time. This is easer said than done. If you have not worked with machine learning before, I'd suggest reading up on that topic a little before diving in.")

### END HINTS ###

    
def on_wine_drop(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name not in data.handled_wines and dat.entity_name.startswith("wine"):
        data.handled_wines.add(dat.entity_name)
        if data.current_label == trigger.entity_name:
            editor.show_vfx(SpawnableVFX.Sparks, editor.get_location(trigger.entity_name))
            data.num_correct += 1
        else:
            editor.show_vfx(SpawnableVFX.ColorBurst, editor.get_location(trigger.entity_name), color=Colors.Black)
            data.num_incorrect += 1

        editor.set_goal_state("acc_goal", GoalState.Success if data.num_incorrect <=3 else GoalState.Fail , f"Classify at most 3 bottles incorrectly. {data.num_incorrect} / {3}")
        editor.set_goal_progress("sort_goal", data.num_correct / N, f"Correctly classify and sort at least {N} wine bottles into their corresponding crates. {data.num_correct} / {N}")
        

### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    #print(f"{entity_type=}, {entity_name=}, {command=}")
    if entity_name == "spawner" and command == "Spawn":
        spawn_next_bottle()

editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###        
        

### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    for t in TriggerZone.find_all():
        t.on_triggered(on_wine_drop)

    
    on_reset()
    editor.set_goal_state("acc_goal", GoalState.Success if data.num_incorrect <=3 else GoalState.Fail , f"Classify at most 3 bottles incorrectly. {data.num_incorrect} / {3}")
    editor.set_goal_progress("sort_goal", data.num_correct / N, f"Correctly classify and sort at least {N} wine bottles into their corresponding crates. {data.num_correct} / {N}")


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    DataExchange.first().editor_store_big_data(CsvDatasets.winequality, wine.iloc[:5500].to_csv().encode("utf-8"))
    RangeFinder.first().editor_set_can_read_feature_data(True)
    RangeFinder.first().editor_set_can_read_entities(True)
    data.reset()
    spawn_next_bottle()
    


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###






# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
import pandas as pd
#load training data
with DataExchange.first().load_big_data(CsvDatasets.winequality) as csv:
    dt_train = pd.read_csv(csv, index_col=[0]) #first col is row number
    #build model...

#get features of wine bottle hit by the range finder
fe = RangeFinder.first()
x = fe.get_feature_data()
name = fe.get_entity_name()

#spawn the next bottle
ObjectSpawner.first().spawn()
