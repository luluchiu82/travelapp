import plotly.express as px
import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, dash_table, callback, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask import Flask, request, render_template

# 導入其他模組中的函數
from src.const import get_constants
from src.generate_visualization import generate_accommodation_bar, generate_transportation_bar, generate_total_cost_bar
from src.data_clean import travel_data_clean, countryinfo_data_clean, data_merge

# 加載欲分析的資料集  
travel_df = pd.read_csv('./data/Travel_dataset.csv')
country_info_df = pd.read_csv('./data/country_info.csv')
attractions_df = pd.read_csv('./data/Attractions.csv')

# 進行資料前處理
travel_df = travel_data_clean(travel_df)
country_info_df = countryinfo_data_clean(country_info_df)

# 合併travel_df和country_info_df，方便後續分析
df_merged = data_merge(travel_df, country_info_df)

# 獲取國家名稱列表
country_list = list(attractions_df['country'].unique())

# 切換頁面（如有需要可以自行增加）
def load_data(tab):
    if tab == 'travel':
        return df_merged
    # elif tab == 'other': # 可以自行增加其他頁面，'other'為頁面名稱，可自行更改設定名稱
    #     return other_df # 此頁面要顯示的資料集

# 呼叫 ./src/const.py 中的 get_constants() 函式，獲取統計數據(畫面上方的四格數據:目的地國家數、旅遊者數、旅遊者國籍數、平均旅遊天數)
num_of_country, num_of_traveler, num_of_nationality, avg_days = get_constants(travel_df)

# 初始化應用程式
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Travel Data Analysis Dashboard', suppress_callback_exceptions=True)
server = app.server

# 生成統計數據的顯示卡片區塊
def generate_stats_card (title, value, image_path):
    return html.Div(
        dbc.Card([ 
            dbc.CardImg(src=image_path, top=True, style={'width': '50px', 'height': '50px','alignSelf': 'center'}), # icon圖片外觀設定
            dbc.CardBody([
                html.P(value, className="card-value", style={'margin': '0px','fontSize': '22px','fontWeight': 'bold'}), # 數據外觀設定
                html.H4(title, className="card-title", style={'margin': '0px','fontSize': '18px','fontWeight': 'bold'}) # 標題外觀設定
            ], style={'textAlign': 'center'}),
        ], style={'paddingBlock':'10px',"backgroundColor":'#ffe5cc','border':'none','borderRadius':'10px'}) # 卡片外觀設定
    )

# 外觀設定
tab_style = {
    'idle':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'backgroundColor': '#ffe5cc',
        'border':'none'
    },
    'active':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'border':'none',
        'textDecoration': 'underline',
        'backgroundColor': '#ffe5cc'
    }
}

MAX_OPTIONS_DISPLAY = 3300

# 定義系統的佈局
app.layout = html.Div([
    dbc.Container([
        # 頂部的切換頁面
        dbc.Row([
            dbc.Col(html.Img(src="./static/image/logo.png", height=100), width=5, style={'marginTop': '15px'}),
            dbc.Col(
                dcc.Tabs(id='graph-tabs', value='overview', children=[
                    dcc.Tab(label='Overview', value='overview', style=tab_style['idle'], selected_style=tab_style['active']),
                    dcc.Tab(label='Attractions', value='attractions', style=tab_style['idle'], selected_style=tab_style['active']),
                ], style={'height': '50px'})
            , width=7, style={'alignSelf': 'center'}),
        ]),
        
        # 統計數據卡片
        dbc.Row([
            dbc.Col(generate_stats_card("Country", num_of_country, "./static/image/earth.svg"), width=3),
            dbc.Col(generate_stats_card("Traveler", num_of_traveler, "./static/image/user.svg"), width=3),
            dbc.Col(generate_stats_card("Nationality", num_of_nationality, "./static/image/earth.svg"), width=3),
            dbc.Col(generate_stats_card("Average Days", avg_days, "./static/image/calendar.svg"), width=3),
        ], style={'marginBlock': '10px'}),

        # 用於顯示不同頁面的內容
        html.Div(id='graph-content')

    ], style={'padding': '0px', 'width': '60%', 'margin': '0 auto'})
], style={'backgroundColor': 'white', 'minHeight': '100vh'})


# 根據選擇的標籤頁更新顯示的內容
@app.callback(
    Output('graph-content', 'children'), # callback function output: id為'graph-content'的 children（第113行程式碼）
    [Input('graph-tabs', 'value')] # callback function input: id為'graph-tabs'的 value值（第87行程式碼）
)
def render_tab_content(tab):
    asian_countries = ['Thailand', 'Indonesia', 'Japan', 'Cambodia', 'South Korea']
    if tab == 'overview':
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3("各國平均每日住宿花費", style={'color': '#ff944d', 'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='dropdown-bar-accommodation',
                        options=[
                            {'label': i, 'value': i} for i in asian_countries
                        ],
                        placeholder='Select a country',
                        style={'width': '60%', 'margin-top': '10px', 'margin-bottom': '10px', 'backgroundColor': 'white', 'color': '#ff944d'}
                    ),
                    dcc.Graph(id='bar-chart-accommodation')
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("各國平均每日交通花費", style={'color': '#ff944d', 'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='dropdown-bar-transportation',
                        options=[
                            {'label': i, 'value': i} for i in asian_countries
                        ],
                        placeholder='Select a country',
                        style={'width': '60%', 'margin-top': '10px', 'margin-bottom': '10px', 'backgroundColor': 'white', 'color': '#ff944d'}
                    ),
                    dcc.Graph(id='bar-chart-transportation')
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("各國平均每日總成本", style={'color': '#ff944d', 'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='dropdown-bar-total',
                        options=[
                            {'label': i, 'value': i} for i in asian_countries
                        ],
                        placeholder='Select a country',
                        style={'width': '60%', 'margin-top': '10px', 'margin-bottom': '10px', 'backgroundColor': 'white', 'color': '#ff944d'}
                    ),
                    dcc.Graph(id='bar-chart-total')
                ])
            ])
        ])

    # 可參考簡報 Callback function (multiValueDropdown.py )
    elif tab == 'attractions':
        # 返回 'Attractions' 頁面的佈局
        return html.Div([
            dcc.Dropdown(
                options=[{'label': country, 'value': country} for country in country_list],
                value=['Australia'],
                id='attractions-dropdown',
                multi=True,  # 啟用多選功能
                style={
                    'backgroundColor': '#ffe5cc',  # 下拉式選單背景顏色
                    'color': 'black'               # 下拉式選單文字顏色
                }
            ),
            html.Div(
                id='attractions-output-container',
                style = {'overflow-x': 'auto'}
            )
        ])
    else:
        return html.Div("選擇的標籤頁不存在。", style={'color': 'black'})

# 可參考簡報Callback function ( dropdown.py )
# 長條圖回調
df = pd.DataFrame(travel_df)

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
#app.layout = html.Div([
#    dcc.Tabs(id='graph-tabs', value='overview', children=[
#        dcc.Tab(label='Overview', value='overview'),
#    ]),
#    html.Div(id='tabs-content')
#])

@app.callback(
    Output('tabs-content', 'children'),
    Input('graph-tabs', 'value')
)
def update_tab(tab):
    return render_tab_content(tab)

@app.callback(
    Output('bar-chart-accommodation', 'figure'),
    Input('dropdown-bar-accommodation', 'value')
)
def update_accommodation_bar(selected_country):
    if not selected_country:
        raise PreventUpdate
    return generate_accommodation_bar(df, selected_country)

@app.callback(
    Output('bar-chart-transportation', 'figure'),
    Input('dropdown-bar-transportation', 'value')
)
def update_transportation_bar(selected_country):
    if not selected_country:
        raise PreventUpdate
    return generate_transportation_bar(df, selected_country)

@app.callback(
    Output('bar-chart-total', 'figure'),
    Input('dropdown-bar-total', 'value')
)
def update_total_cost_bar(selected_country):
    if not selected_country:
        raise PreventUpdate
    return generate_total_cost_bar(df, selected_country)

# 景點下拉式選單回調
@app.callback(
    Output('attractions-output-container', 'children'),
    Input('attractions-dropdown', 'value'),
    Input('graph-tabs', 'value')
)
def update_attractions_output(chosen_countries, tab):
    if tab != 'attractions':
        return no_update
    # 檢查是否有選擇國家
    if not chosen_countries:
        return html.Div("請選擇至少一個國家。", style={'color': 'black'})
    # 過濾出選擇的國家
    chosen_df = attractions_df[attractions_df['country'].isin(chosen_countries)]
    return dash_table.DataTable(
        data=chosen_df.to_dict('records'),
        page_size=10,
        style_data={
            'backgroundColor': '#ffe5cc',
            'color': 'black',
        },
        style_header={
            'backgroundColor': 'white',  # 修改表頭背景顏色
            'color': '#black',          # 修改表頭文字顏色
            'fontWeight': 'bold',
        }
    )

if __name__ == '__main__':
    app.run_server(debug=False)
    
