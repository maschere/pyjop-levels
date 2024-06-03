### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import networkx as nx
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        N = random.randint(11,13)
        G = nx.DiGraph()
        for i in range(N):
            G.add_node(i, loc = Vector3((i-N//2)*3 + random.random(),random.randint(-20,20) + random.random(),random.randint(1,7) + random.random()))
        edges = N+8
        while edges > 0:
            a = random.randint(0, N-1)
            b = a
            while b == a or G.has_edge(b,a):
                b = random.randint(0, N-1)
            G.add_edge(a, b, weight = random.randint(1,3), unweight=1)
            if nx.is_directed_acyclic_graph(G):
                edges -= 1
            else:
                G.remove_edge(a, b)
        G.remove_nodes_from(list(nx.isolates(G)))
        N = G.number_of_nodes() 
        #nx.generate_edgelist(G, data = ["weight"])
        #nx.to_edgelist
        #print(G.nodes)
        # self.source = random.randint(0,G.number_of_nodes()-1)
        # self.target = random.randint(0,G.number_of_nodes()-1)
        # while self.source == self.target:
        #     self.target = random.randint(0,G.number_of_nodes()-1)
        # nx.add_path(G, [self.source,self.target,weight=7)
        # for (u,v,w) in G.edges(data=True):
        #     w['weight'] = random.randint(0,10)
        paths = dict(nx.all_pairs_dijkstra_path_length(G,weight="unweight"))
        pflat:List[Tuple[int,int,int]] = []
        for s in range(N):
            if s not in paths:
                continue
            for t in range(N):
                if t not in paths[s] or paths[s][t] <= 0:
                    continue
                pflat.append((s,t,-paths[s][t]))
                # if paths[s][t] >= N//2-1 and paths[s][t] <= N//2+4:
                #     found = True
                #     print(f"path {s} -> {t} = {paths[s][t]}")
                #     break
        pflat.sort(key=lambda x: x[2])
        #print(pflat)
        s,t,w = pflat[random.randint(0,4)]
        #print(f"path {s} -> {t} = {w}")
        self.graph = G
        self.source = s
        self.target = t
        self.path = list(nx.dijkstra_path(G, self.source,self.target))
        

    def spawn(self):
        # dat = DataExchange.first()
        # e = list(nx.generate_edgelist(self.graph, data=["weight"], delimiter=";"))
        # dat.set_data("network", e)
        #print(e)
        for n in self.graph.nodes(data="loc"):
            n:Tuple[int,Vector3] = n
            col = 0.1
            # if n[0] == self.source:
            #     col = Colors.Darkgreen
            # if n[0] == self.target:
            #     col = Colors.Darkred
            editor.spawn_static_mesh(SpawnableMeshes.Sphere, location=n[1], scale=0.7, material=SpawnableMaterials.SimpleColor, color=col, is_temp=True, rfid_tag=f"node_{n[0]}")
        for e in self.graph.edges.data("weight", default=0.5):
            e:Tuple[int,int,int] = e
            last_loc:Vector3 = self.graph.nodes[e[0]]["loc"]
            loc:Vector3 = self.graph.nodes[e[1]]["loc"]
            
            col = Vector3(0.1,0.12,0.8)/e[2]**2
            # if e[0] in self.path and e[1] in self.path and self.path.index(e[1]) == self.path.index(e[0])+1:
            #     col = Colors.Yellow
            angle = last_loc.find_lookat_rotation(loc)
            mid = last_loc + (loc-last_loc)/2.0
            editor.spawn_static_mesh(SpawnableMeshes.Cube, location = mid, scale = ((loc-last_loc).length, 0.03 * e[2], 0.03 * e[2]), rotation=angle, material = SpawnableMaterials.SimpleEmissive, color = col, is_temp=True, rfid_tag=f"edge_{e[0]}_{e[1]}_{e[2]}")
            editor.spawn_static_mesh(SpawnableMeshes.Cone, location = mid, scale = (0.5), rotation=angle+Vector3(0,-90,0), material = SpawnableMaterials.SimpleEmissive, color = col, is_temp=True)
            
            

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.CpuWorld)
editor.set_map_bounds(extends=Vector3(50,50,20))
editor.spawn_entity(SpawnableEntities.SurveillanceSatellite, "satellite", location=(0,0,18))
editor.spawn_entity(SpawnableEntities.InputBox, "NodeCount", (1.5,-1,0.3))
editor.spawn_entity(SpawnableEntities.InputBox, "WeightSum", (1.5,0,0.5))
editor.spawn_entity(SpawnableEntities.InputBox, "MaxNode", (1.5,1,0.7))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("This a graph. It consists of nodes (the spheres) and weighted, directional edges (the glowing lines with the arrowhead in the middle) between two nodes. Use the SurveillanceSatellite to read the RFID tags with node and edge data of this network graph and solve the tasks below. Enter the solutions in the corresponding InputBox.")

# def sample_goal(goal_name: str):
#     editor.set_goal_progress(
#         goal_name,
#         SimEnvManager.first().get_sim_time() / 30,
#         f"Wait for {int(30)-SimEnvManager.first().get_sim_time()} seconds to complete this level.",
#     )

editor.specify_goal("NodeCount", "How many nodes does this graph have?", hide_next=False, goal_value=0.33)
sleep()
editor.specify_goal("WeightSum", "What is the sum of all edge weights?",hide_next=False, goal_value=0.33)
sleep()
editor.specify_goal("MaxNode", "What is the node with the most outgoing edges?",  hide_next=False, goal_value=0.35)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###


def select_sat(gt:float, num:int, num_revealed:int):
    editor.change_hint(num, """Here is the satellite. It can observe all objects in this level. Retrieve the RFID data of every object like this:
[#9CDCFE](sat) = [#4ABCA5](SurveillanceSatellite).[#DCDCAA](first)\(\)
[#9CDCFE](readings) = [#9CDCFE](sat).[#DCDCAA](get_satellite_data)\(\)
[#C586C0](for) [#9CDCFE](dat) [#C586C0](in) [#9CDCFE](readings):
    [#C586C0](if) [#9CDCFE](dat).rfid_tag:
        [#DCDCAA](print)\([#9CDCFE](dat).rfid_tag\)
""")
    SurveillanceSatellite.first().focus()
editor.add_hint(0,["How does the SurveillanceSatellite work?","Where is the data for the graph?", "How can I get the nodes and edges of this graph?"], on_reveal=select_sat)
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###

def on_input(box:InputBox,gt:float,txt:str):
    val = -1
    if txt != "":
        try:
            val = int(txt)
        except:
            print(f"{txt} is not a valid integer number > 0", col=Colors.Red)
    
    s = GoalState.Open
    if val >= 0:
        if box.entity_name == "NodeCount":
            s = GoalState.Success if data.graph.number_of_nodes() == val else GoalState.Fail
        elif box.entity_name == "WeightSum":
            wieghtsum = sum([e[2] for e in data.graph.edges.data("weight")])
            s = GoalState.Success if wieghtsum == val else GoalState.Fail
            #print(wieghtsum)
        elif box.entity_name == "MaxNode":
            maxnodes = [(i,int(data.graph.out_degree(i))) for i in range(data.graph.number_of_nodes())]
            maxnodes.sort(key=lambda x: x[1], reverse=True)
            maxval = maxnodes[0][1]
            maxnodes_filter = [n[0] for n in maxnodes if n[1]==maxval]
            #print(maxnodes_filter)
            s = GoalState.Success if val in maxnodes_filter else GoalState.Fail

    editor.set_goal_state(box.entity_name, s)
        

def begin_play():
    print("begin play")
    for inp in InputBox.find_all():
        inp.on_changed(on_input)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    data.spawn()
    for inp in InputBox.find_all():
        #on_input(inp, 0, "-1")
        inp.set_text("")
        inp.editor_set_hint_text(f"Enter {inp.entity_name}...")


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
# def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
#     print(f"player command at {gametime}: {entity_type}.{entity_name}.{command}")

# editor.on_player_command(on_player_command)
### END ON PLAYER COMMAND CODE ###

### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
# def on_tick(simtime: float, deltatime: float):
#     if data.time_counter > 5:
#         print("hello every 5 seconds")
#         data.time_counter = 0.0
#     else:
#         data.time_counter += deltatime


# editor.on_tick(on_tick)
### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
#this template code will be provided to the player
#add level specific hints or boilerplate code here.
print("hello world")

env = SimEnvManager.first()

while SimEnv.run_main():
    # main loop to retrieve data from the SimEnv, calculate stuff and send commands back into the SimEnv
    # for example, get current time and display it
    simtime = env.get_sim_time()
    print(f"current time: {simtime} seconds")
