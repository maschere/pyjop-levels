### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
NOTES = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']
NOTES2 = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.next_note:int = 0
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.MuseumHall)
editor.spawn_entity(SpawnableEntities.Piano, "piano", location=(-2.7, 0, 0.1))
editor.spawn_entity(SpawnableEntities.DataExchange,"data", location = (3,3,0))

### END CONSTRUCTION CODE ###

### GOAL CODE ###
target_melody = ['G5', 'Ds4', 'Ds4', 'G5', 'G4', 'As4', 'As4', 'As4', 'G4', 'As4', 'G4', 'As4', 'As4', 'G4', 'As3', 'As4', 'G5', 'G5', 'As4', 'As3', 'As3', 'G5', 'G5', 'As3', 'Gs4', 'As4', 'F5', 'F5', 'As4', 'Gs4', 'Gs4', 'As4', 'F5', 'F5', 'As4', 'Gs4', 'F5', 'D4', 'F5', 'As4', 'Gs4', 'D4', 'Gs4', 'As4', 'As3', 'F5', 'F5']
data.next_note = 0

def melody_goal(goal_name: str):
    editor.set_goal_progress(goal_name,data.next_note/len(target_melody), f"There is song saved in the data exchange. Play all notes of the melody without error. You can vary the tempo as you see fit. \\({data.next_note}/{len(target_melody)}\\)")


editor.specify_goal(
    "melody_goal",
    "Play all notes of the melody without error. You can vary the tempo as you see fit.",
    melody_goal,
    1,
    True,
    False
)
### END GOAL CODE ###

editor.add_hint(0,["The melody numbers mason, what do they mean?!","What are these numbers for the melody?"], "The melody consists of MIDI messages, where each note is encoded as an integer.")
editor.add_hint(1,["How do I convert the MIDI numbers to actual notes?"], "Each note is encoded as a MIDI number from 0 to 127. The middle C3 is number 60 (first note in the 3rd octave).")
editor.add_hint(2,["Listen, I'm neither Beethoven nor Mozart. Give me a formula to convert MIDI."], """[#9CDCFE](midi) = [#B5CEA8](60) [#6A9955](#example MIDI number)
[#9CDCFE](NOTES) = [[#CE9178]('C'), [#CE9178]('Cs'), [#CE9178]('D'), [#CE9178]('Ds'), [#CE9178]('E'), [#CE9178]('F'), [#CE9178]('Fs'), [#CE9178]('G'), [#CE9178]('Gs'), [#CE9178]('A'), [#CE9178]('As'), [#CE9178]('B')]
[#9CDCFE](octave) = [#9CDCFE](midi)//[#DCDCAA](len)\([#9CDCFE](NOTES)\) - [#B5CEA8](2)
[#9CDCFE](note) = [#9CDCFE](midi) % [#DCDCAA](len)\([#9CDCFE](NOTES)\)
[#9CDCFE](notename) = [#4ABCA5](str)\([#9CDCFE](note)\)+[#4ABCA5](str)\([#9CDCFE](octave)\)""")
def play_melody(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, "I'd love to. Here.")
    sleep(1)
    Piano.first().focus()
    for n in target_melody:
        Piano.first().play_note(MusicNotes(n))
        sleep(0.25 + random.uniform(-0.01,0.01))
editor.add_hint(10,["Play the melody for me please."], "...", play_melody)

### DYNAMIC LEVEL CODE ###
def begin_play():
    SmartSpeaker.first().set_volume(0)
    DataExchange.first().set_data("MidiNotes", [91, 75, 75, 91, 79, 82, 82, 82, 79, 82, 79, 82, 82, 79, 70, 82, 91, 91, 82, 70, 70, 91, 91, 70, 80, 82, 89, 89, 82, 80, 80, 82, 89, 89, 82, 80, 89, 74, 89, 82, 80, 74, 80, 82, 70, 89, 89], True)
    print("begin play")
    # sleep(3)
    # editor.play_camera_sequence([
    #     CameraWaypoint([0,0.1,10],[0,-89,-90],0.5),
    #     CameraWaypoint([-2.7,0.1,2],[0,-89,-90],2),
    #     CameraWaypoint([2.7,0.1,2],[0,-89,-90],1),
    #     CameraWaypoint([0,0.1,10],[0,-89,-90],0.5)
    # ])
    
    
editor.on_begin_play(begin_play)
### END DYNAMIC LEVEL CODE ###


### ON LEVEL RESET CODE ###
def on_reset():
    data.reset()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    if command == "PlayNote" and data.next_note < len(target_melody):
        noteval = val.get_string()
        note = MusicNotes(noteval)
        if note == target_melody[data.next_note]:
            data.next_note += 1
        else:
            t = target_melody[data.next_note]
            t = t[0:1] if len(t)==2 else t[0:2]
            noteval = noteval[0:1] if len(noteval)==2 else noteval[0:2]
            tval = -1
            nval = -2
            if t in NOTES:
                tval = NOTES.index(t)
            elif t in NOTES2:
                tval = NOTES2.index(t)
            if noteval in NOTES:
                nval = NOTES.index(noteval)
            elif noteval in NOTES2:
                nval = NOTES2.index(noteval)
            if tval == nval:
                data.next_note += 1
            else:
                data.next_note = 0

editor.on_player_command(on_player_command)

### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
