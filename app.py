import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import base64

from dataContainer import DataContainer

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

colors = {
    'background': '#111111',
    'text': '#000080'
}

uploaded_files = {}
vis_lis = ['BRDF-visualization', 'Integrated', 'CIELAB visualization', 'Color difference calculation']
var_lis = []

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

        html.Hr(),
        html.Div([
            html.Div([
                html.H6('Add and remove data'),

                html.Br([]),

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
                html.H6('Uploaded files'),
                html.Br([]),

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
                html.H6('Visualization'),
                html.P("Select desired visualization method from the list below."),

                dcc.RadioItems(
                    id='visualization-radio',
                    options=[{'label': i, 'value': i} for i in vis_lis],
                    value=vis_lis[0],
                ),
            ], className='six columns'),

            html.Div([
                html.H6('BRDF visualization'),
                html.P("Select variable for BRDF visualization."),

                dcc.Dropdown(
                    id='variable-dropdown',
                    options=[{'label': i, 'value': i} for i in var_lis],
                ),

                html.P("Select polarization for BRDF visualization."),
                dcc.RadioItems(
                    id='polarization',
                    options=[{'label': i, 'value': i} for i in var_lis],
                )

            ], className='six columns')
        ], className="row "),

        html.Hr(),

        dcc.Graph(id='graph')

    ])

    return layout

app.layout = server_layout()

def parse_content(content, name):
    content_type, content_string = content.split(',')
    dc = DataContainer(base64.b64decode(content_string))
    global uploaded_files
    uploaded_files[name] = dc

    return html.Div(
        html.Div('File uploaded'),
    )

def brdf_graph(file, var, pol):
    global uploaded_files
    dc = uploaded_files[file]
    traces = []
    key_variation = dc.data['key_variation']
    z = dc.data_by_key_variation(key_variation, pol)

    traces.append(go.Scatter3d(
            z=z,
            x=dc.x_axis_by_variable('theta_c', pol, len(z)),
            y=dc.y_axis_by_key_variation(key_variation, len(z)),

            mode='markers',
            opacity=0.7,
            marker={
                'size': 12,
                'opacity': 0.7
            },
    ))
    return {
        'data': traces,
        'layout': go.Layout(
            hovermode='closest',
            height=800,
            title='BRDF visualization',
        )
    }

def empty_graph():
    traces = []
    traces.append(go.Scatter(
            x=(0,0,0),
            y=(0,0,0),
    ))
    return {
        'data': traces,
    }

@app.callback(
    Output('data-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def read_data(content, name):
    if content is not None:
        children = [
            parse_content(content, name)
        ]
        return children

@app.callback(
    Output('file-dropdown', 'options'),
    [Input('data-container', 'children'),
     Input('output-container-button', 'children')]
)
def update_file_dropdown(value1, value2):
    return[{'label': i, 'value': i} for i in uploaded_files]

@app.callback(Output('output-container-button', 'children'),
              [Input('remove', 'n_clicks')],
              [State('file-dropdown', 'value')]
)
def remove_file(clicks, value):
    global uploaded_files
    if uploaded_files:
        del uploaded_files[value]
        return 'File "{}" removed from list'.format(value)

@app.callback(Output('graph', 'figure'),
              [Input('visualization-radio', 'value'),
               Input('file-dropdown', 'value'),
               Input('variable-dropdown', 'value'),
               Input('polarization', 'value'),]
)
def update_graph(value, file, var, pol):
    if value == 'BRDF-visualization' and file is not None:
        return brdf_graph(file, var, pol)
    elif value == 'Integrated' and file is not None:
        print('Not yet implemented')
    elif value == 'CIELAB visualization' and file is not None:
        print('Not yet implemented')
    elif value == 'Color difference calculation' and file is not None:
        print('Not yet implemented')
    else:
        return empty_graph()

@app.callback(Output('variable-dropdown', 'options'),
              [Input('file-dropdown', 'value')]
)
def update_variable_dropdown(value):
    global uploaded_files
    if uploaded_files:
        dc=uploaded_files[value]
        var = list(dc.data.keys())
        var.remove('values')
        var.remove('key_variation')
        key_variation = dc.data['key_variation']
        var.remove(key_variation)
        for i in var:
            if len(dc.list_maker(i, 1)) < 2:
                var.remove(i)

        return [{'label': i, 'value': i} for i in var]
    else:
        return [{'label': i, 'value': i} for i in var_lis]

@app.callback(Output('polarization', 'options'),
              [Input('file-dropdown', 'value')]
)
def update_polarization(value):
    global uploaded_files
    if uploaded_files:
        dc = uploaded_files[value]
        if 'polarization' in dc.data:
            options = [
                {'label': 'S', 'value': 's'},
                {'label': 'P', 'value': 'p'},
            ]
            return options

    return [{'label': i, 'value': i} for i in var_lis]

if __name__ == '__main__':
    app.run_server(debug=True)
