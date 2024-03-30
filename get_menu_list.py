import os
import csv
import pandas as pd


def get_menu_list(res_name):
    file_path = f"/Users/atharvmendhe/Documents/Zomato_compatator/RestaurantComparator/Database/Menu/{res_name}_menu.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        menu = list(df["Name"])
    else:
        # need to add a condition if the filepath doesnt exist
        print("File path doesnt exist")

    return menu
