import pandas as pd

def travel_data_clean(travel_df):
    # 去除空值    
    travel_df = travel_df.dropna()

    # 將花費欄位從str轉換成int
    travel_df['Accommodation cost'] = travel_df['Accommodation cost'].str.replace('$', '')
    travel_df['Accommodation cost'] = travel_df['Accommodation cost'].str.replace(',', '')
    travel_df['Accommodation cost'] = travel_df['Accommodation cost'].str.replace(' USD', '')
    travel_df['Accommodation cost'] = travel_df['Accommodation cost'].astype(float)

    travel_df['Transportation cost'] = travel_df['Transportation cost'].str.replace('$', '')
    travel_df['Transportation cost'] = travel_df['Transportation cost'].str.replace(',', '')
    travel_df['Transportation cost'] = travel_df['Transportation cost'].str.replace(' USD', '')
    travel_df['Transportation cost'] = travel_df['Transportation cost'].astype(float)

    # 將日期欄位從str轉換成datetime
    travel_df['Start date'] = pd.to_datetime(travel_df['Start date'])
    travel_df['End date'] = pd.to_datetime(travel_df['End date'])

    # 新增總花費欄位
    travel_df['Total cost'] = travel_df['Accommodation cost'] + travel_df['Transportation cost']

    
    # 將年齡劃分成不同區間 - 10歲一組
    # 先取出最大最小值
    #min_age = travel_df['Traveler age'].min()
    #max_age = travel_df['Traveler age'].max()
    # 以10歲為一組，劃分年齡區間
    #bins = list(range(int(min_age), int(max_age), 10))
    
    # 將年齡區間轉換成str
    #labels = [f'{i}-{i+4}' for i in bins[:-1]]

    # 將 'Traveler age' 分成五個類別
    age_bins = [0, 20, 30, 40, 50, 60]
    age_labels = ['20歲以下', '21-30歲', '31-40歲', '41-50歲', '51-60歲']

    # 將年齡區間Age group新增到DataFrame中
    travel_df['Age group'] = pd.cut(travel_df['Traveler age'], bins=age_bins, labels=age_labels, right=True)
   
    # 計算每個目的地和年齡區間的平均花費
    avg_costs = travel_df.groupby(['Destination', 'Age group'])['Total cost'].mean().reset_index()
    avg_costs.columns = ['Destination', 'Age group', 'Average Cost'] 

    # 合併平均花費到原始資料集
    travel_df = travel_df.merge(avg_costs, on=['Destination', 'Age group'], how='left')

    # 計算每個年齡區間的人數
    age_group_counts = travel_df.groupby('Age group').size().reset_index(name='Age Group Count')

    # 合併年齡區間的人數到資料集
    travel_df = travel_df.merge(age_group_counts, on='Age group', how='left')
    
    # 依照旅遊開始日期劃分月份
    travel_df['Start month'] = travel_df['Start date'].dt.month
    # 將月份轉換成英文
    travel_df['Start month'] = travel_df['Start month'].map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

    return travel_df

def countryinfo_data_clean(countryinfo_df):
    # 去除空值
    countryinfo_df = countryinfo_df.dropna()

    return countryinfo_df

def data_merge(df_travel, df_countryinfo):

    df_countryinfo = df_countryinfo.rename(columns={'Country': 'Destination'})

    df = pd.merge(df_travel, df_countryinfo, on='Destination', how='left')

    return df