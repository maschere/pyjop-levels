### INIT CODE - DO NOT CHANGE ###
from pyjop import *
SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS ###
import random
### END IMPORTS ###
NUM_BOXES = 200
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.mails:list[tuple[str,bool]] = []
        self.invalid = 0
        for i in range(NUM_BOXES):
            domain = random.choice(["de", "com", "co.uk", "io", "org"])
            domain1 = random.choice(["gmail", "gmx", "hotmail", "mail", "freemail"])
            first_name = random.choice(["max","John","emily"])
            last_name = random.choice(["", "smith","mueller","doe"])
            nick_name  = random.choice(["","xxl","pwnz0r","Lucker"])
            suffix  = str(random.randint(0,99999))
            delimiter = random.choice(["","_","."])
            conc = (first_name,nick_name,last_name,suffix)
            mail = delimiter.join((x for x in conc if x)) + "@" + domain1 + "." + domain
            p = random.random()
            is_valid = False
            
            if p > 0.98:
                mail = mail.replace("@", random.choice(["","at","@@","@_@", " ", "ö@", "ß@"]))
            elif p > 0.96:
                mail = mail.replace(".", random.choice(["",";",",","..","0"," "]))
            elif p > 0.94:
                mail += mail
            elif p > 0.92:
                mail = str(random.randint(-9999,99999)) + "@."
            elif p > 0.90:
                mail = ""
            else:
                is_valid = True
            self.mails.append((mail, is_valid))
            if not is_valid:
                self.invalid += 1
            
        self.mails.sort(key = lambda x: random.random())

    def spawn(self):
        for i,v in enumerate(self.mails):
            editor.spawn_static_mesh(SpawnableMeshes.Postbox, f"id{i}", location=(i % 10 -4.5, i // 10 + 0.5 - NUM_BOXES//20, 0), rfid_tag=v[0], material=SpawnableMaterials.SimpleColor, color = Colors.Green if v[1] else Colors.Red, is_temp=True)
            
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(center = (0,0,0), extends=(25,25,16))

editor.spawn_entity(SpawnableEntities.ProximitySensor,"rfidSensor",location = (0,0,0), scale=1.5)
editor.spawn_entity(SpawnableEntities.DataExchange,"result",location = (10,10,0))

        
### END CONSTRUCTION CODE ###

### GOAL CODE ###
def found_invalid() -> float:
    if "invalid" not in DataExchange.first().get_keys():
        return 0.0
    dat = DataExchange.first().get_data("invalid")
    inv = set()
    if hasattr(dat, "__len__"):
        for i in dat:
            try:
                idx = int(i)
            except:
                return -1.0
            if idx < NUM_BOXES and data.mails[idx][1] == False:
                inv.add(idx)
            else:
                return -1.0
    return len(inv) / data.invalid        
    
def invalid_goal(goal_name:str):
    p = found_invalid()
    if p < 0:
        editor.set_goal_state(goal_name, GoalState.Fail)
    else:
        if p < 1:
            editor.set_goal_state(goal_name, GoalState.Open)
        editor.set_goal_progress(goal_name, p)

editor.set_goals_intro_text("Each mail box has an RFID tag with its e-mail address. Around 10% of those addresses are invalid. Identify all invalid e-mail addresses.")
editor.specify_goal("invalid_goal","Enter a list of integers containing the ids of all mail boxes with invalid e-mail addresses into the DataExchange under the key 'invalid'.", invalid_goal)
### END GOAL CODE ###



### ON BEGIN PLAY CODE ###
def begin_play():
    on_reset()
editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    data.reset()
    data.spawn()
    DataExchange.first().remove_data("invalid")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### HINTS ###
editor.add_hint(0,["I identified the invalid e-mails. How do I enter the ids in the DataExchange?"], """Let's assume 'id2' and 'id4' were invalid e-mails:
[#4ABCA5](DataExchange).[#DCDCAA](first)\(\).[#DCDCAA](set_data)\([#CE9178]("invalid"),[[#B5CEA8](2),[#B5CEA8](4)]\)
""")

### LEVEL TICK CODE ###
### END LEVEL TICK CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
