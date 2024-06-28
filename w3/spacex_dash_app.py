# Import required libraries
import pandas as pd
import numpy as np
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
# create parameter
in_ids =['site-dropdown','payload-slider']
out_ids = ['success-pie-chart', 'success-payload-scatter-chart']

#fillout dropdowns option
dropdowns = [{'label': 'All Sites', 'value': 'ALL'}]
for item in list(spacex_df['Launch Site'].unique()):
    dropdowns.append({'label': item, 'value': item})

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard',style={'textAlign': 'center', 'color': '#503D36','font-size': 40}),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id=in_ids[0],
            options=dropdowns,
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True),
        html.Br(),
        
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(
            dcc.Graph(id=out_ids[0])),
        html.Br(),
        html.P("Payload range (Kg):"),
        
        # TASK 3: Add a slider to select payload range
        #dcc.RangeSlider(id='payload-slider',...)
        dcc.RangeSlider(id=in_ids[1],
                min=0, max=10000, step=1000,
                marks={0: '0', 10000: '10000'},
                value=[min_payload, max_payload]),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id=out_ids[1])),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
# define palette color for plot
palette = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261','#e76f51']

@app.callback(Output(component_id=out_ids[0], component_property='figure'),
              Input(component_id=in_ids[0], component_property='value'))             
def get_pie_chart(entered_site):
    #pre filtered data
    filtered_df = spacex_df[['Launch Site','class']]
    all_launch_sites = spacex_df[spacex_df['class']== 1].groupby('Launch Site')['class'].sum().reset_index()
    # if all site from drop down is selected
    if entered_site == 'ALL':
        # create viz
        fig = px.pie(all_launch_sites, values='class', 
                    names='Launch Site', 
                    title='Total Success Launches by Site',
                    color_discrete_sequence=palette)
    else:
        # aggregate data after selected launch site
        filtered_df = filtered_df[filtered_df['Launch Site']== entered_site].groupby(['class']).count().reset_index().sort_values(by=['class'])
        filtered_df.columns = ['class', 'count']
        filtered_df['class'] = np.where(filtered_df['class'] > 0,'success Launches', 'failed Launches' )
        # create viz
        fig = px.pie(filtered_df, values='count',
                     names='class', 
                     title=f"Total Success Launches for site {entered_site}",
                     color_discrete_sequence=palette)

    # config title position of the title of the viz
    fig.update_layout(title_x=0.5, title_font_color="#264653")
    # return the viz
    return fig
        

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id=out_ids[1], component_property='figure'),
              [Input(component_id=in_ids[0], component_property='value'),
              Input(component_id=in_ids[1], component_property='value')])    
def get_pie_chart(entered_site, payload_size):

    # filter data based on selected range of RangeSlide
    selected_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_size[0], payload_size[1])]
    
    # pre defined parameter for viz based on selected condition (site)
    if entered_site == 'ALL':
        titles = 'Correlation between PayLoad and Success for all Sites'
    else:
        selected_df = selected_df[selected_df['Launch Site']== entered_site]
        titles=f'Correlation between PayLoad and Success for Launch Site: {entered_site}'
    
    # create viz
    fig = px.scatter(selected_df, 
                    x='Payload Mass (kg)',
                    y='class',
                    color='Booster Version Category',
                    title=titles,
                    color_discrete_sequence=palette)

    # config title position of the title of the viz               
    fig.update_layout(title_x=0.5, title_font_color="#264653")
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)



