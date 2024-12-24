import pandas as pd

# 上面那一排數據
def get_constants(travel_df):

    # 總旅遊國家數
    num_of_country = travel_df['Destination'].nunique()
    
    # 總旅遊人數
    num_of_traveler = travel_df['Traveler name'].nunique()

    # 總國籍數
    num_of_nationality = travel_df['Traveler nationality'].nunique()

    # 平均旅遊天數
    avg_days = round(float(travel_df['Duration (days)'].mean()), 1)

    return num_of_country, num_of_traveler, num_of_nationality, avg_days