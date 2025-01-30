# leet code like sql / pandas level. mostly abstract, just retrieve the correct answer
import pandas as pd
import numpy as np

products_df = pd.DataFrame([(1,"shirt","red"),(2,"pants","blue")], columns=["product_id","name","color"]).set_index("product_id")
print(products_df)
sales_df = pd.DataFrame([(1,1,10,5.4,"2024-10-15"),(2,1,5,5.1,"2024-10-14"),(3,2,1,15.4,"2024-10-15")], columns=["sale_id","product_id","units","price","date"]).set_index("sale_id")
print(sales_df)

print(products_df.merge(sales_df,"inner",on="product_id"))