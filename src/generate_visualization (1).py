import plotly.express as px
import plotly.colors as colors
import pandas as pd

# 視覺化統計圖

#平均住宿成本
# 長條圖
def generate_accommodation_bar(df, dropdown_value):
    asian_countries = ['Thailand', 'Indonesia', 'Japan', 'Cambodia', 'South Korea']
    if dropdown_value not in asian_countries:
        fig_bar = px.bar(title="請選擇有效的亞洲國家")
        fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
        return fig_bar

    df_group = df[df['Destination'] == dropdown_value]
    average_accommodation_cost = (
        df_group.groupby('Destination')['Accommodation cost']
        .sum() / df_group.groupby('Destination')['Duration (days)'].sum()
    ).reset_index()
    average_accommodation_cost.columns = ['Destination', 'Average Daily Accommodation Cost']
    fig_bar = px.bar(
        average_accommodation_cost, 
        x='Destination', 
        y='Average Daily Accommodation Cost',
        color='Destination',
        title=f'{dropdown_value} - Average Daily Accommodation Cost',
        labels={'Average Daily Accommodation Cost': '平均每日住宿成本', 'Destination': '國家'},
        color_continuous_scale='Viridis'
    )
    fig_bar.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig_bar

def generate_transportation_bar(df, dropdown_value):
    asian_countries = ['Thailand', 'Indonesia', 'Japan', 'Cambodia', 'South Korea']
    if dropdown_value not in asian_countries:
        fig_bar = px.bar(title="請選擇有效的亞洲國家")
        fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
        return fig_bar

    df_group = df[df['Destination'] == dropdown_value]
    average_transportation_cost = (
        df_group.groupby('Destination')['Transportation cost']
        .sum() / df_group.groupby('Destination')['Duration (days)'].sum()
    ).reset_index()
    average_transportation_cost.columns = ['Destination', 'Average Daily Transportation Cost']
    fig_bar = px.bar(
        average_transportation_cost, 
        x='Destination', 
        y='Average Daily Transportation Cost',
        color='Destination',
        title=f'{dropdown_value} - Average Daily Transportation Cost',
        labels={'Average Daily Transportation Cost': '平均每日交通成本', 'Destination': '國家'},
        color_continuous_scale='Viridis'
    )
    fig_bar.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig_bar

def generate_total_cost_bar(df, dropdown_value):
    asian_countries = ['Thailand', 'Indonesia', 'Japan', 'Cambodia', 'South Korea']
    if dropdown_value not in asian_countries:
        fig_bar = px.bar(title="請選擇有效的亞洲國家")
        fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
        return fig_bar

    df_group = df[df['Destination'] == dropdown_value]
    average_total_cost = (
        df_group.groupby('Destination')['Total cost']
        .sum() / df_group.groupby('Destination')['Duration (days)'].sum()
    ).reset_index()
    average_total_cost.columns = ['Destination', 'Average Daily Total Cost']
    fig_bar = px.bar(
        average_total_cost, 
        x='Destination', 
        y='Average Daily Total Cost',
        color='Destination',
        title=f'{dropdown_value} - Average Daily Total Cost',
        labels={'Average Daily Total Cost': '平均每日總成本', 'Destination': '國家'},
        color_continuous_scale='Viridis'
    )
    fig_bar.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig_bar.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig_bar
