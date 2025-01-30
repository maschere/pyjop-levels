### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
import numpy as np
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
N = 365
START_MONEY = 1000.0

def max_prof(prices):
    left = 0 #Buy
    right = 1 #Sell
    max_profit = 0
    iBuy, iSell = -1, -1
    while right < len(prices):
        currentProfit = prices[right] - prices[left] #our current Profit
        if prices[left] < prices[right]:
            if currentProfit > max_profit:
                max_profit = max( currentProfit, max_profit)
                iBuy = left
                iSell = right
        else:
            left = right
        right += 1
    return max_profit, prices[iBuy], iBuy, iSell

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.money = START_MONEY
        self.stock = 0
        self.num_trades = 0
        self.day = 0
        self.price_data:List[float] = [50.0]
        for i in range(1,N):
            p_0 = self.price_data[i-1]
            p_1 = p_0 + random.uniform(-0.5,0.6) + random.normalvariate(0.1,1) + random.choice((-6,-3,1,1,1,2,2,1,1))
            if i > 0.8*N:
                p_1 -= random.normalvariate(1,1)
            if p_1 < 2:
                p_1 = random.uniform(2,5)
            self.price_data.append(p_1)


        #calc best solution
        profit, cost, iBuy, iSell =max_prof(self.price_data)
        num = int(START_MONEY / cost)
        self.max_profit = int(profit * num - random.randint(3,10))

    def place_order(self, buy:bool, amount:int):
        if self.day >= N:
            print("No more days left to trade on", col=Colors.Red)
            return
        cost = amount * self.price_data[self.day]
        if buy and cost <= self.money:
            print(f"Buying {amount} stocks at {self.price_data[self.day]:.2f}$ on day {self.day} -> -{int(amount*self.price_data[self.day])}$", col=Colors.Lightsalmon)
            self.money -= cost
            self.stock += amount
        elif ~buy and amount <= self.stock:
            print(f"Selling {amount} stocks at {self.price_data[self.day]:.2f}$ on day {self.day} -> +{int(amount*self.price_data[self.day])}$", col=Colors.Lightgreen)
            self.money += cost
            self.stock -= amount
        else:
            raise JoyfulException("Invalid order")
        
        self.day += 1
        self.num_trades += 1
        if self.day < N:
            print(f"It is now day {self.day} of {N}.")
        else:
            print("Stock exchange is now closed.")

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)
editor.spawn_entity(SpawnableEntities.DataExchange, "StockMarket", location=(0, 0, 0))
def spawn_temp_object():
    #entities or meshes with is_temp=True are automatically removed on level reset. as such it makes sense to call this function on each level reset to respawn the temp objects in their original location.
    editor.destroy_temporaries()
    minprice = min(data.price_data)
    maxprice = max(data.price_data) -minprice
    for i in range(min(data.day+1,35)):
        val = (data.price_data[data.day-i] - minprice) / maxprice
        editor.spawn_static_mesh(SpawnableMeshes.Cube, location = (-i,-4,val/2), scale = (.5,.5,val*3), material = SpawnableMaterials.SimpleColor, color = (val,0.2,.2), is_temp=True)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###

editor.set_goals_intro_text(f"Let's suppose we can perfectly predict the daily stock price of a company one year in advance. Nice, right? Now it's your task to obtain a maximum profit starting with {START_MONEY}$. Try to place only one buy and one sell order.")

def profit_goal(goal_name: str):
    if data.money-START_MONEY < data.max_profit and data.day >= N:
        editor.set_goal_state(goal_name, GoalState.Fail)
        return
    editor.set_goal_state(goal_name, GoalState.Open)
    editor.set_goal_progress(
        goal_name,
        (data.money-START_MONEY) / data.max_profit,
        f"Make a profit of at least {data.max_profit}$. Currently: {int(data.money-START_MONEY)}$ on day {data.day} of {N}."
    )
    

editor.specify_goal("profit_goal", "Make a profit of at least ...$", profit_goal)
MAX_TRADES = 2
def num_goal(goal_name: str):
    s = GoalState.Open
    if data.num_trades > MAX_TRADES:
        s = GoalState.Fail
    elif data.num_trades > 0:
        s = GoalState.Success
    editor.set_goal_state(
        goal_name,
        s,
        f"Maximum number of trades: {data.num_trades} / {MAX_TRADES}",
    )

editor.specify_goal("num_goal", f"Make at most {MAX_TRADES} trades: {data.num_trades} / {MAX_TRADES}", num_goal, 0, is_optional=True)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How do I buy stocks?", "How do I sell stocks?", "How do I trade?", "Can I hold stocks without buying or selling?"], """Issue an RPC to the DataExchange to either buy, sell or hold:
[#9CDCFE](d) = [#4ABCA5](DataExchange).[#DCDCAA](first)\(\)
[#9CDCFE](d).[#DCDCAA](rpc)\([#CE9178]("buy"), [#B5CEA8](1)\) [#6A9955](#buy 1 stock)
[#9CDCFE](d).[#DCDCAA](rpc)\([#CE9178]("hold"), [#B5CEA8](2)\) [#6A9955](# wait / hold for 2 additional days)
[#9CDCFE](d).[#DCDCAA](rpc)\([#CE9178]("sell"), [#B5CEA8](1)\) [#6A9955](#sell 1 stock)
""")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_rpc_handler(dat, rpc:RPCInvoke):
    buy = rpc.func_name == "buy"
    if rpc.func_name == "buy" or rpc.func_name == "sell":
        try:
            amount = int(rpc.args[0])
            assert(amount>0)
            data.place_order(buy, amount)
        except:
            print("Please specify the amount to buy or sell as the second argument as an integer > 0 and make sure you have enough money / enough stock.", col=Colors.Red)
            return
    elif rpc.func_name == "hold":
        try:
            amount = int(rpc.args[0])
            assert(amount>0)
            data.day += amount
            if data.day > N:
                data.day = N
            print(f"You hodl for {amount} days. It's now day {data.day} of {N}.")
        except:
            print("Please specify the number of days to hold as the second argument as an integer > 0.", col=Colors.Red)
            return
    else:
        print("Unknown rpc. Use 'buy' or 'sell' or 'hold'.", col=Colors.Red)
        return

    d = DataExchange.first()
    d.set_data("CurrentDay", data.day)
    d.set_data("CurrentPrice", data.price_data[data.day])
    spawn_temp_object()
    
def begin_play():
    print("begin play")
    DataExchange.first().on_rpc(on_rpc_handler)
    on_reset()
    


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    d = DataExchange.first()
    d.set_data("PricePrediction", data.price_data)
    d.set_data("CurrentDay", data.day)
    d.set_data("CurrentPrice", data.price_data[data.day])
    spawn_temp_object()


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
print("example rpc to make a trade")
d = DataExchange.first()
d.rpc("buy", 5) #buy 5 socks (automatically advances 1 day)
d.rpc("hold", 10) # wait 10 additional days
d.rpc("sell", 5) #sell 5 stocks  (automatically advances 1 day)

