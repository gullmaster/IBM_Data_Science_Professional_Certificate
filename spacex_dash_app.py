# Import required libraries
import pandas as pd
import dash
#import dash_html_components as html
from dash import html
#import dash_core_components as dcc
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
dropdown_values = pd.DataFrame()
dropdown_values['A'] = spacex_df['Launch Site'].unique()
dropdown_values['B'] = spacex_df['Launch Site'].unique()
data = []
data.insert(0, {'A': 'All Sites', 'B': 'ALL'})
dropdown_values2 = pd.concat([pd.DataFrame(data), dropdown_values], ignore_index=True) # does not save changes to the original dataframe
dropdown_values_dict = dropdown_values2.to_dict('records')

#filtered_df2 = spacex_df[['Launch Site', 'class']]
#filtered_df2 = filtered_df2[filtered_df2['Launch Site'] == 'CCAFS LC-40'].groupby(['class']).count()
#filtered_df2.reset_index(inplace=True)
#print(filtered_df2)
#fig = px.pie(filtered_df2, values='Launch Site', names='class', title='CCAFS LC-40')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[                                                
                                                {'label': i['A'], 'value': i['B']} for i in dropdown_values_dict                                                    
                                            ],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                            min=0,
                                            max=10000,
                                            step=1000,
                                            value=[min_payload, max_payload]
                                            ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):    
    filtered_df = spacex_df[['Launch Site', 'class']]

    if entered_site == 'ALL':
        df1 = filtered_df.groupby(['Launch Site']).mean()
        df1.reset_index(inplace=True)
        fig = px.pie(df1, values='class', names='Launch Site', title='Distribution of successful launches by site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        df2 = filtered_df[filtered_df['Launch Site'] == entered_site].groupby(['class']).count()
        df2.reset_index(inplace=True)        
        fig = px.pie(df2, values='Launch Site', names='class', title='Succes rate for site: ' + entered_site)
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value"))
def get_scatter_chart(entered_site, entered_payload):
    filtered_df = spacex_df[['Launch Site', 'Payload Mass (kg)', 'class', 'Booster Version Category']]

    if entered_site == 'ALL':
        df = filtered_df[
            (filtered_df['Payload Mass (kg)'] >= int(entered_payload[0]))
            & (filtered_df['Payload Mass (kg)'] <= int(entered_payload[1]))
            ]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title = 'Success payload for all sites')
        return fig
    else:
        df = filtered_df[
            (filtered_df['Launch Site'] == entered_site)
            & (filtered_df['Payload Mass (kg)'] >= int(entered_payload[0]))
            & (filtered_df['Payload Mass (kg)'] <= int(entered_payload[1]))
            ]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title = 'Success payload for site: ' + entered_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()