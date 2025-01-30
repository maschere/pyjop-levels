### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
def lin2val(idx):
    rank = idx % 13
    suit = idx // 13
    return int(rank * 100 + suit)

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.money = 100
        self.last_card = -1
        self.current_card = -1
        self.bet_amount = 0
        self.bet_higher = False
        self.shuffle = list(range(52))
        self.shuffle.sort(key=lambda x: random.random())
        self.num_bets = 0

    def next_card(self):
        card = PlayingCard.first()
        self.last_card = self.current_card
        self.current_card = self.shuffle.pop()
        # (int(rank)-2) + 13*int(suit) 
        card.set_card(self.current_card)
        if self.last_card == -1:
            return
        valcurr = lin2val(self.current_card)
        vallast = lin2val(self.last_card)
        
        if (self.bet_higher==True and valcurr > vallast) or (self.bet_higher==False and valcurr < vallast):
            self.money += 2*self.bet_amount
            print(f"You won {self.bet_amount}", col=Colors.Green)
        else:
            print(f"You lost {self.bet_amount}", col=Colors.Darkorange)

        self.num_bets += 1    
        self.bet_amount = 0
        
        if len(self.shuffle) < 10:
            print("Reshuffling whole deck")
            self.shuffle = list(range(52))
            self.shuffle.sort(key=lambda x: random.random())

    def place_bet(self, amount:int, bet_higher:bool) -> bool:
        if amount > self.money:
            print(f"Bet too large. You only have {self.money} left", col = Colors.Yellow)
            return False
        if amount < 1:
            print(f"You must bet at least 1.", col = Colors.Yellow)
            return False
        self.money -= amount
        self.bet_amount = amount
        self.bet_higher = bet_higher
        return True
        

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)
editor.set_map_bounds(center = (0,0,0), extends=(16,16,12))
editor.spawn_entity(SpawnableEntities.PlayingCard, "Card", location=(0, 0+5, 1.01), scale=10, is_controllable=False)
editor.spawn_entity(SpawnableEntities.InputBox, "BetAmount", location=(0.6, 5.0, 0.95))
editor.spawn_entity(SpawnableEntities.PushButton, "BetHigh", location=(0, -0.7+5, 1.05))
editor.spawn_entity(SpawnableEntities.PushButton, "BetLow", location=(0, 0.7+5, 1.05))
editor.spawn_entity(SpawnableEntities.DataExchange, "Bookie", location=(-3, 5, 0), is_controllable=False)
editor.spawn_static_mesh(SpawnableMeshes.Cube, scale= (1.5,3,2), location=(0, 5, 0), material=SpawnableMaterials.SimpleColor, color=(0.1,0.1,0.12))
editor.spawn_static_mesh(SpawnableMeshes.Cube, scale= (1.5,3,1.9), location=(-3, 3, 0), material=SpawnableMaterials.SimpleColor, color=(0.1,0.1,0.12))
editor.spawn_entity(SpawnableEntities.SmartSpeaker, "music", location=(0.1, -1.25, 1.05))

def vis_money():
    DataExchange.first().set_data("Points", data.money)
    m = data.money
    bars = m // 4000
    m -= bars*4000
    e50 = m  // 50
    m -= e50 * 50
    e20 = m // 20
    m -= e20 * 20
    e1 = m
    editor.destroy_temporaries()
    sleep()
    for i in range(bars):
        editor.spawn_static_mesh(SpawnableMeshes.Goldbar, location=(random.uniform(-3-.2,-3+.2),random.uniform(3-0.5,3+0.5)-0.2,random.uniform(2.4,3)), is_temp=True, simulate_physics=True, adjust_coll=True)
    for i in range(e50):
        editor.spawn_static_mesh(SpawnableMeshes.BankNoteEuro50, location=(random.uniform(-3-.2,-3+.2)+0.6,random.uniform(3-0.5,3+0.5),random.uniform(2,2.2)), is_temp=True, simulate_physics=True, adjust_coll=True, scale=0.3)
    for i in range(e20):
        editor.spawn_static_mesh(SpawnableMeshes.BankNoteEuro20, location=(random.uniform(-3-.2,-3+.2),random.uniform(3-0.5,3+0.5)+0.2,random.uniform(2.3,3)), is_temp=True, simulate_physics=True, adjust_coll=True, scale=0.3)
    for i in range(e1):
        editor.spawn_static_mesh(SpawnableMeshes.CoinEuro1, location=(random.uniform(-3-.2,-3+.2),random.uniform(3-0.5,3+0.5)+.3,random.uniform(2.5,3)), is_temp=True, simulate_physics=True, adjust_coll=True, scale=0.3)

    
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
editor.set_goals_intro_text("Let's play a simple betting game. Look at the current card from a standard 52 playing card deck. Will the next card be [*bold](higher) or [*bold](lower)? Place any bet amount and win double or nothing. Cards are drawn without replacement, but once the deck is below 10 cards it will be reshuffled.")

def fast_goal(goal_name:str):
    s = GoalState.Open
    if data.num_bets > 30:
        s = GoalState.Fail
    elif data.num_bets > 0:
        s = GoalState.Success
    editor.set_goal_state(goal_name, s, f"Place at most 30 bets. Number of bets: {data.num_bets}/30")
    
editor.specify_goal("fast_goal", "Place at most 30 bets.", fast_goal, 0, is_optional=True)


def earn_goal(goal_name: str):
    editor.set_goal_progress(
        goal_name,
        (data.money+data.bet_amount) / 1e5,
        f"Place bets until you have at least 100000 points. Current Points: {data.money+data.bet_amount}"
    )

editor.specify_goal("earn_goal", "Place bets until you have at least 100000 points.", earn_goal)


### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How do I place a bet?"], """Enter a betting amount in the InputBox:
[#4ABCA5](InputBox).[#DCDCAA](first)\(\).[#DCDCAA](set_text)\([#B5CEA8](100)\)
Then press either the "BetHigh" or the "BetLow" button, depending on your guess for the next card.""")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_press_handler(sender:PushButton, simtime:float):
    try:
        amount = int(InputBox.first().get_text())
    except:
        print("Invalid bet amount. Please enter an integer number.", col=Colors.Red)
    if data.place_bet(amount, sender.entity_name.endswith("BetHigh")):
        #print("Drawing next card...")
        #editor.show_vfx(SpawnableVFX.Smoke, editor.get_location("Card"))
        #sleep(0.6)
        data.next_card()
        vis_money()
        
def begin_play():
    print("begin play")
    SmartSpeaker.first().set_sound_by_name(BuiltinMusic.PianoPlaylist)
    for btn in PushButton.find_all():
        btn.on_press(on_press_handler)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    data.next_card()
    vis_money()
    InputBox.first().editor_set_hint_text("bet amount?")


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###

#get current rank and suit of card
rank,suit = PlayingCard.first().get_current_card()
print(f"Rank: {rank}, Suit: {suit}")

