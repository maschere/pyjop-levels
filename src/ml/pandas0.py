# leet code like sql / pandas level. mostly abstract, just retrieve the correct answer

### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_synthetic_data(num_products=100, num_sales=5000):
    # Create products DataFrame
    product_ids = range(1, num_products + 1)
    base_prices = np.random.uniform(10, 1000, num_products).round(2)
    
    products = pd.DataFrame({
        'product_id': product_ids,
        'base_price': base_prices,
        'color': np.random.choice(["red", "green", "blue"], num_products)
    })
    
    # Create Sales DataFrame
    sale_ids = range(1, num_sales + 1)
    sale_product_ids = np.random.choice(product_ids, num_sales)
    
    # Create a temporary DataFrame to join products and sales
    temp_sales = pd.DataFrame({
        'product_id': sale_product_ids
    })
    
    # Merge to get the correct base prices for each sale
    temp_sales = temp_sales.merge(products[['product_id', 'base_price']], on='product_id', how='left')
    
    # Generate sale prices with some variation from base price
    sale_prices = np.random.uniform(0.8, 1.2, num_sales) * temp_sales['base_price'].values
    sale_prices = sale_prices.round(2)
    
    sale_units = np.random.randint(1, 11, num_sales)
    
    # Generate dates within the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    sale_dates = [start_date + timedelta(days=np.random.randint(0, 366)) for _ in range(num_sales)]
    
    sales = pd.DataFrame({
        'sale_id': sale_ids,
        'product_id': sale_product_ids,
        'sale_price': sale_prices,
        'sale_units': sale_units,
        'sale_date':  sale_dates
    })
    
    return products, sales

# Create the DataFrames
NUM_SALES = 5000
NUM_PROD = 100


class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()

        self.products_df, self.sales_df = create_synthetic_data(NUM_PROD, NUM_SALES)

        #find num red products above price 500

        self.num_red500 = self.products_df.loc[(self.products_df["base_price"] > 500) & (self.products_df["color"] == "red")].product_id.count()

        #calculate the total revenue for sale with id 128
        rev_sale_id = 128
        self.total_rev_for_id = (self.sales_df.loc[self.sales_df["sale_id"]==rev_sale_id].sale_price * self.sales_df.loc[self.sales_df["sale_id"]==rev_sale_id].sale_units).sum()

        #calc average sale_price for red products sold in December.
        sales_dat = self.sales_df.merge(self.products_df, on='product_id', how='inner')
        self.avg_price_red_dec = sales_dat.loc[(sales_dat.sale_date.dt.month==12) & (sales_dat.color == "red")].sale_price.mean()

        #calculate number of units sold with price more than 10% of base price
        sales_dat["sale_pric_pct"] = sales_dat["sale_price"] / sales_dat["base_price"]
        self.sum_units_above10 = sales_dat.loc[sales_dat.sale_pric_pct > 1.1].sale_units.sum()

        #get the sale date with the highest total revenue
        sales_dat["rev"] = sales_dat["sale_price"] * sales_dat["sale_units"]
        self.best_sale_date = sales_dat.groupby("sale_date").sum().sort_values("rev", ascending=False).index[0].strftime("%Y-%m-%d")



data = DataModel()


# Display the first few rows of each DataFrame
# print("\nProducts DataFrame shape:", data.products_df.shape)
# print(data.products_df.head())
# print("\nSales DataFrame shape:", data.sales_df.shape)
# print(data.sales_df.head())

# Display the shapes of the DataFrames
editor.select_map(SpawnableMaps.CpuWorld)
editor.spawn_entity(SpawnableEntities.DataExchange, "data")
editor.spawn_entity(SpawnableEntities.InputBox, "aNumRed500", (1.5,-1,0.3))
editor.spawn_entity(SpawnableEntities.InputBox, "bTotalRevenueForSaleId", (1.5,0,0.5))
editor.spawn_entity(SpawnableEntities.InputBox, "cAvgPriceDecember", (1.5,1,0.7))


editor.set_goals_intro_text("Let's work with a small database and pandas. Retrieve the two DataFrames 'products' and 'sales' from the DataExchange and answer the following questions by submitting their answers in their respective InputBox.")



editor.specify_goal("aNumRed500", "How many products are color red and have a base price above 500 ?", goal_value=0.34, hide_next=False)
editor.specify_goal("bTotalRevenueForSaleId", "What is the total revenue for the sale with id 128 ?", goal_value=0.34, hide_next=False)
editor.specify_goal("cAvgPriceDecember", "What is the average sale price of red products sold in December?", goal_value=0.34, hide_next=False)


def on_input(box:InputBox,gt:float,txt:str):
    val = -1.0
    if txt != "":
        try:
            val = float(txt)
            assert(val>0)
        except:
            print(f"{txt} is not a valid number >0", col=Colors.Red)
            return
    
    
    s = GoalState.Open
    if val>0:
        if box.entity_name == "aNumRed500":
            s = GoalState.Success if data.num_red500 == int(val) else GoalState.Fail
        elif box.entity_name == "bTotalRevenueForSaleId":
            s = GoalState.Success if abs(data.total_rev_for_id - val) < 0.1 else GoalState.Fail
            #print(wieghtsum)
        elif box.entity_name == "cAvgPriceDecember":
            s = GoalState.Success if abs(data.avg_price_red_dec - val) < 0.1 else GoalState.Fail

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
    DataExchange.first().set_data("products", data.products_df.to_json(date_format="iso"))
    DataExchange.first().set_data("sales", data.sales_df.to_json(date_format="iso"))
    for inp in InputBox.find_all():
        inp.set_text("")
        inp.editor_set_hint_text(f"Enter {inp.entity_name}...")
editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###

### END LEVEL TICK CODE ###


# set editor template code
editor.set_template_code(from_comment="### PLAYER TEMPLATE CODE ###")


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###


### PLAYER TEMPLATE CODE ###
import pandas as pd

print("hello world")

env = SimEnvManager.first()

#load the products table using pandas read_json
products_df = pd.read_json(DataExchange.first().get_data("products"))
print(products_df.head())
