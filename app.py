import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import base64

from DataContainer import DataContainer
from UIupdater import UIupdater, brdfUpdater

#App configurations
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
colors = {'background': '#111111', 'text': '#000080'}

#Global variables
uploaded_files = {}
vis_lis = ['BRDF-visualization', 'Integrated', 'CIELAB visualization', 'Color difference calculation']
var_lis = []

#App layout
#Page divided half (six columns)
def server_layout():
    layout = html.Div([
        html.H1(children='BiRD view',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }),
        html.Div(children='''A web application for data visualization.''',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }),

        html.Hr(),
        html.Div([
            html.Div([
                html.H4('Add and remove data'),
                html.P("Upload new file by clicking Upload file button.\
                       Remove file by selecting it from the list and clicking Remove file button."),

                dcc.Upload(
                    html.Button('Upload File'),
                    id='upload-data',
                    style={
                        'marginTop': 25,}
                ),
                html.Div(id='data-container'),
                html.Br([]),
                html.Button('Remove file', id='remove'),
                html.Div(id='output-container-button',
                         children='Select file and press remove'),

            ], className='six columns'),

            html.Div([
                html.H4('Uploaded files'),
                dcc.Dropdown(
                    id='file-dropdown',
                    options=[{'label': i, 'value': i} for i in uploaded_files],
                    clearable=False,
                ),
            ], className='six columns')
        ], className="row "),

        html.Hr(),
        html.Div([
            html.Div([
                html.H4('Visualization'),
                html.P("Select desired visualization method from the list below."),
                dcc.RadioItems(
                    id='visualization-radio',
                    options=[{'label': i, 'value': i} for i in vis_lis],
                    value=vis_lis[0],
                ),
            ], className='six columns'),
            html.Div([
                html.H4('Variables'),
                html.Div(id='variable', style={'display': 'none'}),
                html.Div(id='radio', style={'display': 'none'}),
                html.Div(id='menu'),
            ], className='six columns')
        ], className="row "),

        html.Hr(),
        dcc.Graph(id='graph')
    ])
    return layout

app.layout = server_layout()

#Parses uploaded file
def parse_content(content, name):
    content_type, content_string = content.split(',')
    dc = DataContainer(base64.b64decode(content_string))
    global uploaded_files
    uploaded_files[name] = dc
    return html.Div(html.Div('File uploaded'))

#Empty graph for starting app
def empty_graph():
    traces = []
    traces.append(go.Scatter(
            x=(0, 0, 0),
            y=(0, 0, 0),
    ))
    return {'data': traces}

#Updates page according to events
@app.callback(
    Output('data-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')])
def read_data(content, name):
    if content is not None:
        children = [
            parse_content(content, name)
        ]
        return children

@app.callback(
    Output('file-dropdown', 'options'),
    [Input('data-container', 'children'),
     Input('output-container-button', 'children')])
def update_file_dropdown(value1, value2):
    return[{'label': i, 'value': i} for i in uploaded_files]

@app.callback(Output('output-container-button', 'children'),
              [Input('remove', 'n_clicks')],
              [State('file-dropdown', 'value')])
def remove_file(clicks, value):
    global uploaded_files
    if uploaded_files:
        del uploaded_files[value]
        return 'File "{}" removed from list'.format(value)

@app.callback(Output('graph', 'figure'),
              [Input('visualization-radio', 'value'),
               Input('file-dropdown', 'value'),
               Input('variable', 'value'),
               Input('radio', 'value')])
def update_graph(value, file, var, pol):
    if value == 'BRDF-visualization' and file is not None:
        updater = brdfUpdater(file, uploaded_files)
        return updater.brdf_graph(var, pol)
    elif value == 'Integrated' and file is not None:
        return empty_graph()
    elif value == 'CIELAB visualization' and file is not None:
        return empty_graph()
    elif value == 'Color difference calculation' and file is not None:
        return empty_graph()
    else:
        return empty_graph()

@app.callback(Output('menu', 'children'),
              [Input('visualization-radio', 'value'),
               Input('file-dropdown', 'value')])
def update_menu(value, file):
    if value == 'BRDF-visualization' and file is not None:
        updater = brdfUpdater(file, uploaded_files)
        return updater.brdf_menu()
    elif value == 'Integrated' and file is not None:
        return 'Not yet implemented'
    elif value == 'CIELAB visualization' and file is not None:
        return 'Not yet implemented'
    elif value == 'Color difference calculation' and file is not None:
        return 'Not yet implemented'
    else:
        return 'File not found'

if __name__ == '__main__':
    app.run_server(debug=True)