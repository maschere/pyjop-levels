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
        #print(self.path)
        self.failed = False
        self.waypoints:set[str] = set()
        self.finished = False
        

    def spawn(self):
        #dat = DataExchange.first()
        #e = list(nx.generate_edgelist(self.graph, data=["weight"], delimiter=";"))
        #dat.set_data("network", e)
        #print(e)
        for n in self.graph.nodes(data="loc"):
            n:Tuple[int,Vector3] = n
            col = 0.1
            nodename = f"node_{n[0]}"
            if n[0] == self.source:
                col = Colors.Darkgreen
                editor.set_location("crane", n[1])
                nodename = f"source_node_{n[0]}"
                #AirliftCrane.first().set_target_location(n[1])
            else:
                editor.spawn_entity(SpawnableEntities.TriggerZone, f"trigger_point_{n[0]}", location=n[1], scale = 1.7, is_temp=True, is_clickable=False, is_readable=False, is_controllable=False)
            if n[0] == self.target:
                col = Colors.Darkred
                nodename = f"target_node_{n[0]}"
            editor.spawn_static_mesh(SpawnableMeshes.Sphere, location=n[1], scale=0.7, material=SpawnableMaterials.SimpleColor, color=col, is_temp=True, rfid_tag=nodename)
            
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
editor.spawn_entity(SpawnableEntities.AirliftCrane, "crane", location=(0,0,20))
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text("Use the SurveillanceSatellite to get the nodes and edges of this network graph.")

def path_goal(goal_name: str):
    if data.failed or SimEnvManager.first().get_sim_time() < 1.0:
        return

    if not data.finished:
        loc = editor.get_location("crane")
        min_dist = 100.0
        for i in range(len(data.path)-1):
            n0 = data.path[i]
            n1 = data.path[i+1]
            l0:Vector3 = data.graph.nodes[n0]["loc"]
            l1:Vector3 = data.graph.nodes[n1]["loc"]
            d = Vector3.distance_to_line(l0,l1,loc)
            if d < min_dist:
                min_dist = d

        #print(min_dist)

        if min_dist > 0.5:
            data.failed = True
            editor.set_goal_state(goal_name, GoalState.Fail)
        
    #get all 
    editor.set_goal_progress(
        goal_name,
        len(data.waypoints) / (len(data.path)-1)
    )

editor.specify_goal("path_goal", "Move the AirliftCrane along the edges from the green node to the red node. Use the shortest possible edge path and do not deviate more than 50cm from it.", path_goal)

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

def begin_play():
    print("begin play")
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###
def on_waypoint(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name == "crane" and not data.failed and not data.finished and trigger.entity_name not in data.waypoints:
        data.waypoints.add(trigger.entity_name)
        if len(data.waypoints) >= len(data.path)-1:
            data.finished = True
            editor.show_vfx(SpawnableVFX.Fireworks1, location = editor.get_location("crane") - [0,0,5])

### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    data.spawn()
    editor.set_goal_state("path_goal", GoalState.Open)
    sleep(1)
    for t in TriggerZone.find_all():
        editor.set_hidden(t.entity_name, True)
        editor.set_clickable(t.entity_name, False)
        t.on_triggered(on_waypoint)


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


### ON PLAYER COMMAND CODE - Add code that should be executed each time the player issues a code command to an entity
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
