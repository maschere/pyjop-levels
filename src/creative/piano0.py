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
        self.note_count:int = 0
        

data = DataModel()
### END DATA MODEL ###

### CONSTRUCTION CODE ###
editor.select_map(SpawnableMaps.MuseumHall)
editor.spawn_entity(SpawnableEntities.Piano, "piano", location=(-2.7, 0, 0.1))

### END CONSTRUCTION CODE ###

### GOAL CODE ###
def melody_goal(goal_name: str):
    editor.set_goal_progress(goal_name,data.note_count/50.0, f"Play a little melody of at least 50 notes. \\({data.note_count}/50\\)")


editor.specify_goal(
    "melody_goal",
    "Play a little melody of at least 50 notes.",
    melody_goal,
    1,
    True,
    False
)
### END GOAL CODE ###

editor.add_hint(0,["How can I play notes programmatically?","Do I have to press 50 keys manually?"], """You can play notes programmatically with python. Here is an example snippet:
[#9CDCFE](piano) = [#4ABCA5](Piano).[#DCDCAA](first)\(\)
[#C586C0](for) [#9CDCFE](i) [#C586C0](in) [#DCDCAA](range)\([#B5CEA8](10)\):
    [#9CDCFE](piano).[#DCDCAA](play_note)\([#4ABCA5](MusicNotes).[#B5CEA8](C5)\)
    [#DCDCAA](sleep)\([#B5CEA8](1)\)""")

editor.add_hint(2,["Playing the same note over and over again is boring. How to make things more interesting?"], """Glad you asked. While you can complete the level by simply playing the same note 50 times, it's a lot more fun to play semi-random notes and add semi-random pauses between them. Here is snippet to get you started:
[#C586C0](import) [#DCDCAA](random)
[#9CDCFE](notes) = [[#CE9178]("C"),[#CE9178]("D"),[#CE9178]("E"),[#CE9178]("F"),[#CE9178]("G"),[#CE9178]("A"),[#CE9178]("B")]
[#9CDCFE](length) = [[#B5CEA8](1),[#B5CEA8](0.5),[#B5CEA8](0.25)]
[#9CDCFE](octave) = [#B5CEA8](4)
[#9CDCFE](piano) = [#4ABCA5](Piano).[#DCDCAA](first)\(\)

[#C586C0](while) [#4ABCA5](SimEnv).[#DCDCAA](run_main)\(\):
    [#9CDCFE](piano).[#DCDCAA](play_note_in_octave)\([#DCDCAA](random).[#DCDCAA](choice)\([#9CDCFE](notes)\),[#9CDCFE](octave)\)
    [#DCDCAA](sleep)\([#DCDCAA](random).[#DCDCAA](choice)\([#9CDCFE](length)\)\)
    [#C586C0](if) [#DCDCAA](random).[#DCDCAA](random)\(\) > [#B5CEA8](0.6):
        [#9CDCFE](octave) += [#DCDCAA](random).[#DCDCAA](randint)\(-[#B5CEA8](1),[#B5CEA8](1)\)
        [#C586C0](if) [#9CDCFE](octave) < [#B5CEA8](1):
            [#9CDCFE](octave) = [#B5CEA8](1)
        [#C586C0](elif) [#9CDCFE](octave) > [#B5CEA8](7):
            [#9CDCFE](octave) = [#B5CEA8](7)""")


### DYNAMIC LEVEL CODE ###
def begin_play():
    print("begin play")
    SmartSpeaker.first().set_volume(0)
    on_reset()
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
    if command == "PlayNote":
        data.note_count += 1

editor.on_player_command(on_player_command)

### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
