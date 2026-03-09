import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import regex
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_bootstrap_components as dbc

dane=pd.read_csv('dane_bkg.csv', index_col=0)
dane_rh=pd.read_csv('dane_rh.csv', index_col=0)
dane_compton=pd.read_csv('dane_compton.csv', index_col=0)
energia=[ round(x*0.02009, 2) for x in range(2048)]
pierwiastki=pd.read_csv('pierwiastki.csv', index_col=0)
pierwiastki_rh=pd.read_csv('pierwiastki_rh.csv', index_col=0)
pierwiastki_compton=pd.read_csv('pierwiastki_compton.csv', index_col=0)

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])#
server = app.server


app.layout =dbc.Container(
    [
    html.H1('DRANGSONG Manuscripts -XRF analysis', style={'marginTop':'50px'}),
    html.H2('Wybierz próbki do wyświetlenia', style={'marginTop':'50px'}),
    html.Div([
        dcc.Checklist(
            options=dane.columns,
            value=['1f.2'],
            id='sample',
            style={'display': 'grid', 'grid-template-columns': 'repeat(20, 1fr)'}
        )], style={'width':'100%'}),
    html.H2('Wybierz dane:', style={'marginTop':'50px'}),
    dcc.RadioItems(
        options=[
            {'label': 'dane nieznormalizowane', 'value': 'dane'},
            {'label': 'dane znormalizowane do rodu', 'value': 'dane_rh'},
            {'label': 'dane znormalizowane do Comptona', 'value': 'dane_compton'}
        ],
        value='dane_rh',
        id='data_frame'
    ),
    dcc.Graph(id='graph_spectrum'),
    html.Br(),
    html.H2("Wybierz dane:", style={'marginTop':'20px'}),
    html.H6("Ze zbioru usunięto outliery: 8(reddish), 36, 59f.8, 98, 135f.1, 219, 250"),
    html.Div([
        dcc.Dropdown(
          options=pierwiastki.columns,
          value='Al',
          id='pierwiastek1',
          style={'width':'100px', 'marginRight':'2px'}
        ),
        dcc.Dropdown(
          options=pierwiastki.columns,
          value='Al',
          id='pierwiastek2',
          style={'width':'100px'}
        )], style={'display': 'flex'}),
    dcc.RadioItems(
        options=[
            {'label': 'dane nieznormalizowane', 'value': 'pierwiastki'},
            {'label': 'dane znormalizowane do rodu', 'value': 'pierwiastki_rh'},
            {'label': 'dane znormalizowane do Comptona', 'value': 'pierwiastki_compton'}
          ],
        value='pierwiastki',
        id='data_frame2'
        ),
    dcc.Graph(id='graph_pairplot')],
    fluid=True,
    className="px-3"
    )

@app.callback(
    Output('graph_spectrum', 'figure'),
    Input('sample','value'),
    Input('data_frame', 'value')
)
def draw_single(sample_list, data_frame_name):
  # Map the string ID to the actual DataFrame
  data_frames = {'dane': dane, 'dane_rh': dane_rh, 'dane_compton': dane_compton}
  selected_df = data_frames[data_frame_name]
  elements={'Al':1.49, 'Si':1.73, 'S':2.31, 'K':3.31, 'Ca':3.69, 'Ti':4.50, 'Mn':5.89, 'Fe':6.39, 'Cu':8.02, 'Zn':8.64, 'Hg':9.98, 'Pb':10.55, 'Sr':14.12}
  fig=go.Figure()
  for i in sample_list:
    fig.add_trace((go.Scatter(x=energia, y=selected_df[i], name=i)))
    fig.update_xaxes(title_text='E [KeV]', range=(0,16))
    fig.update_yaxes(title_text='counts')
    fig.update_layout(width=1200, height=600)
    if len(sample_list)==1:
      fig.update_layout(title=i)

  for key, value in elements.items():
    fig.add_vline(x=value,line_width=6, opacity=0.2)
    fig.add_annotation(text=key,
                  yref="paper",
                  x=value, y=1.05, showarrow=False)


  return fig

@app.callback(
    Output('graph_pairplot', 'figure'),
    Input('pierwiastek1','value'),
    Input('pierwiastek2', 'value'),
    Input('data_frame2', 'value')
)

def draw_pair(pierwiastek1, pierwiastek2, dane):
  data_frames2 = {'pierwiastki': pierwiastki, 'pierwiastki_rh':  pierwiastki_rh, 'pierwiastki_compton':  pierwiastki_compton}
  selected_df2 = data_frames2[dane]
  fig=px.scatter(data_frame=selected_df2, x=pierwiastek1, y=pierwiastek2, hover_name=selected_df2.index)
  fig.update_layout(width=600, height=500)
  fig.update_xaxes(title_text=pierwiastek1)
  fig.update_yaxes(title_text=pierwiastek2)

  return fig

port = int(os.environ.get("PORT", 8050))
app.run(jupyter_mode="external", host="0.0.0.0", port=port, debug=True)

