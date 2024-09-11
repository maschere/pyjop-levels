### INIT CODE - DO NOT CHANGE ###
from pyjop import *
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
import math
import numpy as np
### END IMPORTS ###
GOLDSMITHS = ["Humick","Gokhabera","Dalondretrud","Ustrahulda","Whurhana","Throzmoren","Werangrounelyn","Kokurum","Weramnaestr","Lovroure"]
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.num_rpc =0
        self.num_guess =0
        self.cheater = random.choice(GOLDSMITHS)
        self.user_guess = ""
        

data = DataModel()

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.MedievalCourtyard)
editor.spawn_entity(SpawnableEntities.DigitalScale,"scales",location = (0.2,0,0))
editor.spawn_entity(SpawnableEntities.DataExchange,"data",location = (3,3,0))

def smith_gold(smith:str, weight:float):
    if weight <= 0.00000001 or weight > 100:
        print(f"Weight must be greater than 0 and less than 100 kg", col = Colors.Orange)
        return
    l = weight**(1.0/3.0)    
    s = [l/2,l/2,l/2]
    if data.cheater == smith:
        weight *= 0.9
        s[random.randint(0,2)] *= 0.9
    loc = (random.uniform(-0.5,1.4),random.uniform(-0.3,0.3),random.uniform(2.5,4.5))
    editor.spawn_static_mesh(SpawnableMeshes.Goldbar,weight=weight, scale = s, is_temp = True, location = loc, simulate_physics=True, adjust_coll=True)
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def SmithingGoal(goal_name:str):
    s = GoalState.Open
    txt = "Identify the cheating goldsmith."
    if data.user_guess == data.cheater:
        s = GoalState.Success
    elif data.user_guess in GOLDSMITHS:
        s = GoalState.Fail
    elif data.user_guess:
        txt += f" [yellow]({data.user_guess}) is not one of the smiths. Check the list of available goldsmiths in the DataExchange."
    editor.set_goal_state(goal_name,s)

editor.set_goals_intro_text("There are 10 goldsmiths. One of them is a cheat who always uses [red](10% less gold) than what you pay for. You can commission the smiths to forge gold bars \(for any amount of gold to any number of goldsmiths\). Use the data exchange to make the commision with an [red](rpc call). See template code \(use clear if already filled\) for an example.")
editor.specify_goal("SmithingGoal","Identify the cheating goldsmith.", SmithingGoal)

def opt_goal(goal_name:str):
    s = GoalState.Open
    if data.num_rpc == 1 and data.num_guess == 1:
        s = GoalState.Success
    elif data.num_rpc > 1 or data.num_guess > 1:
        s = GoalState.Fail
    editor.set_goal_state(goal_name,s)
    
editor.specify_goal("opt_goal","Make only a single rpc call to commission the smiths and only make another single rpc call to identify the cheater.", opt_goal, 0, True, True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant in-game. ###
editor.add_hint(0,["What is an RPC?","What does RPC stand for?"], "RPC is short for remote procedure call. It means calling a procedure or function that is located on another resource (other process, other computer, cloud server, ...). Here you use an RPC to order from the goldsmiths and identify the cheater.")

editor.add_hint(2,["How can I commision the goldsmiths?", "Show me a code example to order from the goldsmiths."], """[#9CDCFE](dat) = [#4ABCA5](DataExchange).[#DCDCAA](first)\(\)
[#6A9955](#order and make goldbars)
[#9CDCFE](dat).[#DCDCAA](rpc)\([#CE9178]("order"), [#9CDCFE](Humick) = [#B5CEA8](5.0), [#9CDCFE](Gokhabera) = [#B5CEA8](4.0)\)""")
editor.add_hint(3,["I figured out who cheated! How do I tell the system who the cheating goldsmith is?"], """Assuming Humick is the cheater, here is how you'd do it:
[#9CDCFE](dat) = [#4ABCA5](DataExchange).[#DCDCAA](first)\(\)
[#9CDCFE](dat).[#DCDCAA](rpc)\([#CE9178]("cheater"), [#CE9178]("Humick")\)""")

editor.add_hint(5,["It is impossible to figure out the cheater with one single call!","Please provide a hint how to solve this puzzle with a single rpc call."], """To figure out who the cheater is with one rpc call, you have to commission all goldsmiths at once.""")
editor.add_hint(6,["Okay, but if I commission all goldsmiths with the same amount, how can I figure out who the cheat is?"], """You can't. I repeat. You cannot figure out who the cheat is if you commission all goldsmiths with the [red](same amount).""")

editor.add_hint(8,["How can I measure the goldbars that I have created?"], """Use the digital scale available to you. You can simply look at the display to the see the total weight, or do it programmatically:
[#9CDCFE](w) = [#4ABCA5](DigitalScale).[#DCDCAA](first)\(\).[#DCDCAA](get_weight)\(\)""")

### ON BEGIN PLAY CODE ###
def begin_play():
    dat = DataExchange.first()
    dat.on_rpc(on_rpc)
    dat.set_data("goldsmiths", GOLDSMITHS)
    on_reset()
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint((0.2,0.000,-1),[0,-89,0],1.5),
    #     CameraWaypoint((0.2,0.000,8.500),[0,-89,0],2.2),
    #     CameraWaypoint((0.000,0.000,-1),[0,-89,179],1.7)
    # ])
    # sleep(1.2)
    # for s in GOLDSMITHS:
    #     smith_gold(s,5)
    #     sleep(0.15)
    
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


def on_rpc(dat:DataExchange,rpc:RPCInvoke):
    if rpc.func_name == "order" and len(rpc.kwargs)>0:
        data.num_rpc += 1
        for k,v in rpc.kwargs.items():
            if k in GOLDSMITHS:
                smith_gold(k, v)
            else:
                print(f"Unknown goldsmith: {k}", col=Colors.Orange)
        dat.return_rpc(rpc.func_name, True)
    elif rpc.func_name == "order" and len(rpc.args) == 1:
        data.num_rpc += 1
        for k,v in rpc.args[0].items():
            if k in GOLDSMITHS:
                smith_gold(k, v)
            else:
                print(f"Unknown goldsmith: {k}", col=Colors.Orange)
        dat.return_rpc(rpc.func_name, True)
    elif rpc.func_name == "cheater" and len(rpc.args) == 1:
        if data.num_rpc < 1:
            print("Please commission the goldsmiths before trying to identify the cheater.", col=Colors.Orange)
            return
        data.user_guess = rpc.args[0]
        data.num_guess += 1
        dat.return_rpc(rpc.func_name, True)
    else:
        print(f"Error: Unknown RPC '{rpc.func_name}'. Available RPCs: 'order', 'cheater'. Example usage: dat.rpc(\"order\", Humick = 5.0, Gokhabera = 4.0); dat.rpc(\"cheater\", \"Humick\")", col=Colors.Orange)
        dat.return_rpc(rpc.func_name, False)


### ON LEVEL RESET CODE ###
def on_reset():
    data.reset()
    
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###

editor.set_template_code(from_comment="### RPC example")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### RPC example
dat = DataExchange.first()
scale = DigitalScale.first()
#order and make goldbars
dat.rpc("order", Humick = 5.0, Gokhabera = 4.0)
sleep(2)
#use the scale to (somehow) figure out who the cheater is by weighing the gold bars
print(scale.get_weight())
#call out cheater once you identified them
dat.rpc("cheater", "Humick")