import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

class UIupdater():
    def __init__(self, file, uploaded_files):
        self.dc = uploaded_files[file]

class brdfUpdater(UIupdater):
    #def __init__(self, file):
    #    self.ui = UIupdater(file)

    def brdf_graph(self, var, pol):
        traces = []
        z = self.dc.data_by_key_variation(pol)

        traces.append(go.Scatter3d(
                z=z,
                x=self.dc.x_axis_by_variable('theta_c', pol, len(z)),   #theta_c should be replaced with var
                y=self.dc.y_axis_by_key_variation(len(z)),
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 12,
                    'opacity': 0.7
                }))
        return {
            'data': traces,
            'layout': go.Layout(
                hovermode='closest',
                height=800,
                title='BRDF visualization',
        )}

    def brdf_menu(self):
        var = list(self.dc.data.keys())
        var.remove('values')
        var.remove('key_variation')
        key_variation = self.dc.data['key_variation']
        var.remove(key_variation)
        for i in var:
            if len(self.dc.list_maker(i, 1)) < 2:
                    var.remove(i)

        if 'polarization' in self.dc.data:
            options = [
                {'label': 'S', 'value': 's'},
                {'label': 'P', 'value': 'p'},
            ]
        else:
            options = []

        return html.Div([
            html.H6('BRDF visualization'),
            html.P("Select variable for BRDF visualization."),
            dcc.Dropdown(
                id='variable',
                options=[{'label': i, 'value': i} for i in var],
            ),
            html.P("Select polarization for BRDF visualization."),
            dcc.RadioItems(
                id='radio',
                options=options,
        )])