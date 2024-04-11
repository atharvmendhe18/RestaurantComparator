from fuzzywuzzy import fuzz
import os
import pandas as pd

project_directory = os.path.dirname(os.path.abspath(__file__))


def suggest_dishes_fuzzy(user_input, df_menu):
    similarities = []
    for index, row in df_menu.iterrows():
        dish_name = row["Name"]
        # Calculate similarity score using Levenshtein distance
        score = fuzz.ratio(user_input.lower(), dish_name.lower())
        if score > 50:
            similarities.append([dish_name, row["Price"]])

    # Sort by similarity score
    similarities.sort(key=lambda x: x[0], reverse=True)
    return similarities


def compare_menus(res_list, dish_to_compare):
    similar_dishes = []
    for res in res_list:
        df_res = pd.read_csv(f"{project_directory}/Database/Menu/{res}_menu.csv")
        similar_dishes.append(suggest_dishes_fuzzy(dish_to_compare, df_res))

    print(len(similar_dishes))

    return similar_dishes


# res_list = ['priyanka_pure_veg_restaurant','sai_prakash','hotel_mamta_dining_bar']

# compare_menus(res_list,'paneer butter')
