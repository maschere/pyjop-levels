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
        self.setosa_correct = 0
        self.virginica_correct = 0
        self.versicolor_incorrect = 0
        self.handled_flowers:set[str] = set()
        self.num_setosa = 0
        self.num_virginica = 0
        self.num_versicolor = 0
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.GrasslandOutdoor)
editor.spawn_entity(SpawnableEntities.RangeFinder,"FeatureExtractor",location = (0,-3,0.2), rotation = (0,0,180))
editor.spawn_entity(SpawnableEntities.MovablePlatform,"platform",location = (0,-3,0.2))
editor.spawn_entity(SpawnableEntities.DataExchange, "Database", location=(0, 5, 0))
f = editor.get_dataset_file(CsvDatasets.iris)
iris = pd.read_csv(f).sample(frac=1, ignore_index=True)
def spawn_temp_object():
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it makes sense to call this function on each level reset to respawn the temp objects in their original location.
    idx = random.sample(range(120,149),k=20)
    orig = Vector3(5,-3,0.7) - (0,-3,0.2)
    for i,row in enumerate(idx):
        x = iris.loc[row, iris.columns != "variety"].to_dict()
        y = iris.loc[row, ["variety"]].item().lower()
        mesh = SpawnableMeshes.Flower1
        s = 2
        if y == "setosa":
            mesh = SpawnableMeshes.Flower2
            s = 1
            data.num_setosa += 1
        elif y == "versicolor":
            mesh = SpawnableMeshes.Flower3
            data.num_versicolor += 1
        else:
            data.num_virginica += 1

          
        #calc circle pos
        pos = orig.rotate_vector(Rotator3(0,0,i/20 * 360)) + (0,-3,0.2)
        
        editor.spawn_static_mesh(mesh, f"flower{i}", location=pos, scale=s, is_temp=True)
        editor.spawn_static_mesh(SpawnableMeshes.FlowerPot, location=pos.xy, scale=(2,2,2.5), is_temp=True)

    if data.num_setosa > 1:
        data.num_setosa -= 1
    if data.num_virginica > 1:
        data.num_virginica -= 1
    sleep(0.5)
    for i,row in enumerate(idx):
        x = iris.loc[row, iris.columns != "variety"].to_dict()
        y = iris.loc[row, ["variety"]].item().lower()
        editor.set_feature_data(f"flower{i}", x , y)

    

        
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def goals_up():
    p = data.setosa_correct / max(1,data.num_setosa)
    editor.set_goal_progress("setosa_goal", p, f"Harvest Setosa plants. Currently: {data.setosa_correct} / {data.num_setosa} harvested.")
    p = data.virginica_correct / max(1,data.num_virginica)
    editor.set_goal_progress("virginica_goal", p, f"Water Virginica plants. Currently: {data.virginica_correct} / {data.num_virginica} watered.")
    s = GoalState.Success
    if data.versicolor_incorrect > 1:
        s = GoalState.Fail
    editor.set_goal_state("versicolor_goal", s)

editor.set_goals_intro_text("In the DataExchange there is a small dataset with 4 measurements of 120 iris plants of 3 different varieties [darkgray](Setosa, Versicolor, Virginica). We have collected 20 new samples of iris plants and you need to harvest all Setosa plants, give the Virginica plants some water and do nothing with the Versicolor plants. You may make 1 mistake for each flower type. See your example code how to harvest/water the flowers.")
editor.specify_goal("setosa_goal", "Harvest Setosa plants.", None, 0.5, hide_next=False)
editor.specify_goal("virginica_goal", "Water Virginica plants.", None, 0.5, hide_next=False)
editor.specify_goal("versicolor_goal", "Ignore Versicolor plants.", None, 0, is_optional=True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How can I determine the type of flower?"], "The range finder is equipped with a feature extractor, that can extract certain measurements for each flower you point it at. Based on the reference dataset in the DataExchange, you can compute a statistical learning model that should be able to classify the flowers correctly most of the time. This is easer said than done. If you have not worked with machine learning before, I'd suggest reading up on that topic a little before diving in.")

### END HINTS ###


def on_rpc_handler(dat, rpc:RPCInvoke):
    predicted_label = ""
    if rpc.func_name == "harvest":
        predicted_label = "setosa"
    elif rpc.func_name == "water":
        predicted_label = "virginica"
    else:
        print(f"Invalid rpc '{rpc.func_name}'. Available rpcs: harvest, water", col=Colors.Red)
        return
    flower = str(rpc.args[0])
    label = editor.get_feature_target(flower)
    if not label:
        print(f"You specified an invalid flower name: {flower} . You must provide a valid flower name (e.g. 'flower0') as the only parameter to the 'harvest' or 'water' rpc functions.", col=Colors.Red)
        return

    if flower in data.handled_flowers:
        print(f"You already handled {flower}", col=Colors.Red)
        return
    data.handled_flowers.add(flower)

    #spawn effect
    if rpc.func_name == "water":
        editor.show_vfx(SpawnableVFX.WaterJet, editor.get_location(flower) + (0,0,0.7), rotation=(0,-80,0))
    elif rpc.func_name == "harvest":
        editor.show_vfx(SpawnableVFX.ColorBurst, editor.get_location(flower) + (0,0,0.1), color=Colors.Brown)
        editor.destroy(flower)
    
    if predicted_label == label:
        if label =="setosa":
            data.setosa_correct += 1
        elif label == "virginica":
            data.virginica_correct += 1
    else:
        if label == "versicolor":
            data.versicolor_incorrect += 1
    goals_up()
        
    
    


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def begin_play():
    print("begin play")
    DataExchange.first().on_rpc(on_rpc_handler)
    
    
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    DataExchange.first().editor_store_big_data(CsvDatasets.iris, iris.iloc[:120].to_csv().encode("utf-8"))
    RangeFinder.first().editor_set_can_read_feature_data(True)
    RangeFinder.first().editor_set_can_read_entities(True)
    data.reset()
    platform = MovablePlatform.first()
    platform.editor_set_rotation_limits([0,0,360])
    platform.editor_set_location_limits([0,0,0])
    platform.attach_entities()
    spawn_temp_object()
    editor.set_goal_state("setosa_goal", GoalState.Open)
    editor.set_goal_state("virginica_goal", GoalState.Open)
    editor.set_goal_state("versicolor_goal", GoalState.Open)
    goals_up()
    


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###






# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
import pandas as pd
#get training data
with DataExchange.first().load_big_data(CsvDatasets.iris) as csv:
    dt_train = pd.read_csv(csv, index_col=[0]) #first col is row number
    #build model...

#get features of flower hit by range finder
fe = RangeFinder.first()
x = fe.get_feature_data()
name = fe.get_entity_name()

#predict flower class....

#use rpc to water or harvest the plant
dat = DataExchange.first()
dat.rpc("water", name)
#dat.rpc("harvest", name)
