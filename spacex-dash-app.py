# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
data_path = "spacex_launch_dash.csv"
spacex_df = pd.read_csv(data_path)
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            *[
                {'label': site, 'value': site}
                for site in spacex_df['Launch Site'].unique()
            ]
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show total successful launches per site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Add a Range Slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show correlation between payload and success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: callback for the success pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Total successes by site
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure for a specific site
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = df['class'].value_counts().rename({0: 'Failure', 1: 'Success'})
        fig = px.pie(
            names=counts.index,
            values=counts.values,
            title=f'Success vs. Failure for site {entered_site}'
        )
    return fig

# TASK 4: callback for the success-payload scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # filter by payload range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=(
            'Payload vs. Outcome for All Sites' if entered_site == 'ALL'
            else f'Payload vs. Outcome for {entered_site}'
        )
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8052, debug=True)
