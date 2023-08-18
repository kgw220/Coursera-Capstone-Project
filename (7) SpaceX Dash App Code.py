# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout as a skeleton for the UI of the application
# Html breaks used in between each major component of the app to properly
# divide them up
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        ],
                                             # what the input defaults to
                                             value ='ALL',
                                             # what is shown in the dropdown textbox if nothing is selected
                                             placeholder="Input what site(s) you want to look at", 
                                             # Setting this to true allows us to enter keywords to search launch sites
                                             searchable=True
                                    ),

                                html.Br(),

                    # Adds a pie chart to show the total successful launches count for all sites
                    # If a specific launch site was selected, show the Success vs. Failed counts for the site
                    html.Div(dcc.Graph(id='success-pie-chart')),
                    html.Br(),

                    # P tag is paragraph tag
                    html.P("Payload range (Kg):"),
                    # TASK 3: Add a slider to select payload range
                    # dcc.RangeSlider(id='payload-slider',...)

                    dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    # marks={0: '0', 100: '100'},
                                    value=[min_payload, max_payload]),

                    # Add a scatter chart to show the correlation between payload and launch success
                    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
# Specifying output name means the figure returned maps to that name
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', #automatically graphs when class = 1
        names = 'Launch Site', 
        title = 'Success Count for all launch sites')
        return fig #returns it under the component_id 'success-pie-chart'
    else:
        # return the outcomes piechart for a selected site
        # use conditional to get a filtered_df with just the specified launch site data
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Returns a new df with just the launch site, class, and count 
        # of class via groupby (like a groupby SQL query)
        filtered_df = filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')

        # values specified what is being graphed, name indicates the legend
        fig = px.pie(filtered_df,values = 'class count',names='class',title=f"Total Success Launches for site {entered_site}")
        return fig #returns it under the component_id 'success-pie-chart'

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Function decorator to specify function input and output
# Specifying output name means the figure returned maps to that name
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, slider):
    # Returns a new df that fulfills the condition of being between the specified range 
    # indicated by the slider. The endpoints of the values are specified in a two element array.
    filtered_df = spacex_df[(slider[0] <= spacex_df['Payload Mass (kg)']) & (spacex_df['Payload Mass (kg)'] <= slider[1])]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                          # Color parameter allows you to add more data 
                          # to each data point for distinction
                          color='Booster Version Category',
                          title='Launch Success Rate For All Sites')
        return fig
    else:
        # use conditional to get a filtered_df with just the specified launch site data
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                          # Color parameter allows you to add more data 
                          # to each data point for distinction
                          color='Booster Version Category',
                          title='Launch Success Rate For ' + entered_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()