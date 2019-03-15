import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import base64

from DataContainer import DataContainer

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

colors = {
    'background': '#111111',
    'text': '#000080'
}

def server_layout():
    layout = html.Div([
        html.H1(children='BiRD view',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
        ),

        html.Div(children='''
                A web application for data visualization.''',
                style={
                'textAlign': 'center',
                'color': colors['text']
                }
        ),

        html.Div(children='''
            First step: Download data''',
                 style={
                     'textAlign': 'center',
                     'color': colors['text']
                 }
        ),

        dcc.Upload(
            html.Button('Upload File'),
            id='upload-data',
            style={
                'textAlign': 'center',
                'marginTop': 25,
            }
        ),

        html.Div(id='data-container', style={'display': 'none'}),
        html.Div(id='x-selector1', style={'display': 'none'}),
        html.Div(id='pol-selector', style={'display': 'none'}),

        html.Div(id='menu1'),
        html.Div(id='graph1')

    ], style={"padding-top": "20px"})

    return layout

app.layout = server_layout()

def menu(content):
    content_type, content_string = content.split(',')
    dc = DataContainer(base64.b64decode(content_string))
    var = list(dc.data.keys())

    var.remove('values')
    var.remove('key_variation')
    key_variation = dc.data['key_variation']
    var.remove(key_variation)
    for i in var:
        if len(dc.list_maker(i, 1)) < 2:
            var.remove(i)

    if 'polarization' in dc.data:
        var.remove('polarization')
        return html.Div([
            html.Label('Second step: Select variable for x-axis. Variable of y axis is the key variation.',
                       style={
                           'textAlign': 'center',
                           'color': colors['text'],
                           'marginTop': 20
                       }
                       ),
            dcc.Dropdown(
                id='x-selector1',
                options=[{'label':i, 'value':i} for i in var],
                value=var[1],
                clearable=False,
                style={
                    'marginLeft': 50,
                    'marginRight': 50
                }
            ),
            html.Label('Select polarization',
                       style={
                           'textAlign': 'center',
                           'color': colors['text'],
                           'marginTop': 20
                       }
                       ),
            dcc.RadioItems(
                id='pol-selector',
                options=[
                    {'label': 'S', 'value': 's'},
                    {'label': 'P', 'value': 'p'},
                ],
                value='s',
                style={
                    'textAlign': 'center',
                }
            ),
        ])
    else:
        return html.Div([
            html.Label('Second step: Select variable for x-axis. Variable of y axis is the key variation.',
                       style={
                           'textAlign': 'center',
                           'color': colors['text'],
                           'marginTop': 20
                       }
                       ),
            dcc.Dropdown(
                id='x-selector1',
                options=[{'label':i, 'value':i} for i in var],
                value=var[1],
                clearable=False,
                style={
                    'marginLeft': 50,
                    'marginRight': 50
                }
            ),
            html.Div(id='pol-selector', style={'display': 'none'}),
        ])


def make_graph(content, var, pol):
    content_type, content_string = content.split(',')
    dc = DataContainer(base64.b64decode(content_string))
    traces = []
    key_variation = dc.data['key_variation']

    traces.append(go.Scatter3d(
            z=dc.data_by_key_variation(key_variation, pol),
            x=dc.x_axis_by_variable('theta_c', pol, len(dc.data_by_key_variation(key_variation,pol))),
            y=dc.y_axis_by_key_variation(key_variation, len(dc.data_by_key_variation(key_variation, pol))),

            mode='markers',
            opacity=0.7,
            marker={
                'size': 12,
                'colorscale': 'Viridis',
                'opacity': 0.7
            },
    ))
    return html.Div([
        dcc.Graph(id='angle-graph',
                  figure={'data': traces,
                          'layout': {
                              'height': 800,
                              'title': '3D graph',
                              'xaxis': {
                                  'title': var
                              },
                              'yaxis': {
                                  'title': key_variation
                              },
                              'zaxis': {
                                  'title': 'Measured value'
                              }
                          }
                  }
        ),
        ])

@app.callback(
    Output(component_id='data-container', component_property='children'),
    [Input(component_id='upload-data', component_property='contents')]
)
def read_data(content):
    if content is not None:
        return content

@app.callback(
    Output(component_id='menu1', component_property='children'),
    [Input(component_id='data-container', component_property='children')]
)
def create_menu(content):
    if content is not None:
        children = [
            menu(content)
        ]
        return children

@app.callback(
    Output(component_id='graph1', component_property='children'),
    [Input(component_id='x-selector1', component_property='value'),
     Input(component_id='pol-selector', component_property='value')],
    [State(component_id='data-container', component_property='children')]
)
def makeGraph(var, pol, content):
    if content is not None:
        children = [
            make_graph(content, var, pol)
        ]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)