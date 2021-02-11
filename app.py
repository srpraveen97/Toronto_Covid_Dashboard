import pandas as pd
import numpy as np
import plotly.express as px  
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# ----------------------------------------------------------------------------

# Import dataset from the open data portal
data = pd.read_csv("https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv")
df1 = data.copy()
df2 = data.copy()

# Number of confirmed and probable cases
confirmed_cases = data['Classification'].value_counts()[0]
probable_cases = data['Classification'].value_counts()[1]
active_cases = data['Outcome'].value_counts()[1]
fatal_cases = data['Outcome'].value_counts()[2]
resolved_cases = data['Outcome'].value_counts()[0]

# Removing the points with no age data
df1 = df1[df1['Age Group'].notna()]

# Removing the points with no FSA data
df2 = df2[df2['FSA'].notna()]

# Preparing data for map plot
fsa_out = df2.groupby(['FSA','Outcome']).size()

count_act = []
count_fat = []
count_res = []

for code in list(df2['FSA'].unique()):
    try:
        count_act.append(fsa_out[code]['ACTIVE'])
    except:
        count_act.append(0)
        
for code in list(df2['FSA'].unique()):
    try:
        count_fat.append(fsa_out[code]['FATAL'])
    except:
        count_fat.append(0)
        
for code in list(df2['FSA'].unique()):
    try:
        count_res.append(fsa_out[code]['RESOLVED'])
    except:
        count_res.append(0)
        
count_act = np.array(count_act)
count_fat = np.array(count_fat)
count_res = np.array(count_res)

total_count = count_act + count_fat + count_res

count_data = pd.DataFrame({'CFSAUID':list(df2['FSA'].unique()),'ACTIVE':count_act,'FATAL':count_fat,
                          'RESOLVED':count_res,'TOTAL':total_count})

with open('GeoJSON/Toronto_fsa.geojson') as f:
  Toronto_fsa = json.load(f)
  

# Preparing data for the final plot

age_out = df1.groupby(['Age Group','Outcome']).size() 

act = np.array([age_out[age]['ACTIVE'] for age in list(df1['Age Group'].unique())])
fat = np.array([age_out[age]['FATAL'] for age in list(df1['Age Group'].unique())])
res = np.array([age_out[age]['RESOLVED'] for age in list(df1['Age Group'].unique())])
tot = act + fat + res
per_fat = 100*fat/tot

Age_data = pd.DataFrame({'Age_Group':list(df1['Age Group'].unique()),'Count_resolved':res,'Count_fatal':fat,
                         'Count_active':act,'Total_Count':tot,'Percent_fatal':per_fat})

Age_data = Age_data.reindex([7,1,5,6,0,2,4,3,8])


# Unique values for outcome and adding an option of total cases
option = [{'label':x, 'value':x} for x in df1['Outcome'].unique()]
option.append({'label':'TOTAL', 'value':'TOTAL'})

# Unique values for outcome and adding an option of total cases
option1 = [{'label':'RESOLVED', 'value':'RESOLVED'},{'label':'FATAL', 'value':'FATAL'}]
option1.append({'label':'TOTAL', 'value':'TOTAL'})

# Create options for age group
option2 = [{'label':x, 'value':x} for x in Age_data['Age_Group'].unique()]
option2.append({'label':'ALL', 'value':'ALL'})


# ----------------------------------------------------------------------------
# Dashboard Layout

# Meta_tags ensures that it is responsive to phones, tablets too!
# For various stylesheets visit the website https://www.bootstrapcdn.com/bootswatch/

# Cheatsheet for bootstrap https://hackerthemes.com/bootstrap-cheatsheet/#text-secondary

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])

server = app.server

app.layout = dbc.Container([
    
    dbc.Row([
        
        dbc.Col(html.H1("Tracking Covid-19 cases in Toronto",
                        className = 'text-center text-uppercase, mb-4'),
                width = 12)
        
            ]),
    
    
    dbc.Row([
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [html.H4(id="card-conf", children=[], className = 'mb-4')
                     ])
                    )], #width = {'size':2, 'offset':1}
            xs = 12, sm =12, md = 12, lg = 2, xl = 2),
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [html.H4(id="card-prob", children=[], className = 'mb-4')
                     ])
                    )], #width = {'size':2}
            xs = 12, sm =12, md = 12, lg = 2, xl = 2),
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [html.H4(id="card-act", children=[], className = 'mb-4')
                     ])
                    )], #width = {'size':2}
            xs = 12, sm =12, md = 12, lg = 2, xl = 2),
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [html.H4(id="card-fat", children=[], className = 'mb-4')
                     ])
                    )], #width = {'size':2}
            xs = 12, sm =12, md = 12, lg = 2, xl = 2),
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    [html.H4(id="card-res", children=[], className = 'mb-4')
                     ])
                    )], #width = {'size':2}
            xs = 12, sm =12, md = 12, lg = 2, xl = 2)
        
            ], justify='center'),

    
    dbc.Row([
        
        dbc.Col([
            
            html.H4('Distribution of Covid-19 cases in Toronto'),
            dcc.RadioItems(id='fsa_map', value='TOTAL',
                         options=option, className='text-light', labelStyle={'display': 'inline-block'},
                         labelClassName = 'mr-3'),
            dcc.Graph(id='map', figure={})
            ], #width = {'size':5,'offset':1},
            xs = 12, sm =12, md = 12, lg = 5, xl = 5),
        
        dbc.Col([
            
            html.H4('Covid-19 progression over time'),
            dcc.RadioItems(id='daily_cases', value='TOTAL',
                         options=option1, className='text-light', labelStyle={'display': 'inline-block'},
                         labelClassName = 'mr-3'),
            dcc.Graph(id='timeseries', figure={})
            ], #width = {'size':5}
            xs = 12, sm =12, md = 12, lg = 5, xl = 5)
        
        ], className = 'pt-md-5', justify='center'),
    
    
    dbc.Row([
        
        dbc.Col([
            
            html.H4('Source of Infection for various Age Groups'),
            dcc.Dropdown(id='contact_mode',multi=False, value='ALL',
                         options=option2, className='text-dark'),
            dcc.Graph(id='lineplot', figure={})
            ], #width = {'size':5,'offset':1}
            xs = 12, sm =12, md = 12, lg = 5, xl = 5),
        
        dbc.Col([
            
            html.H4('Total cases and fatality for different Age Groups'),
            dcc.Graph(id='static', figure={})
            ], #width = {'size':5}
            xs = 12, sm =12, md = 12, lg = 5, xl = 5)
        
        ], className = 'pt-md-5 mb-4', align = 'center', justify='center')
    
    
    ], fluid = True)


# ----------------------------------------------------------------------------

@app.callback(
    [Output('card-conf','children'), Output('card-prob','children'), Output('card-act','children'),
      Output('card-fat','children'), Output('card-res','children'), Output('map','figure'),
      Output('timeseries','figure'), Output('lineplot','figure'), Output('static','figure')],
    [Input('fsa_map','value'), Input('daily_cases','value'),Input('contact_mode','value')]
    )

def update_graph( outcome_ , daily_ , agegroup_):
    
    print(outcome_)
    print(type(outcome_))
    
    print(daily_)
    print(type(daily_))
    
    print(agegroup_)
    print(type(agegroup_))
    
    string1 = 'Confirmed Cases: {}'.format(confirmed_cases)
    string2 = 'Probable Cases: {}'.format(probable_cases)
    string3 = 'Active Cases: {}'.format(active_cases)
    string4 = 'Fatal Cases: {}'.format(fatal_cases)
    string5 = 'Resolved Cases: {}'.format(resolved_cases)

    fig1 = px.choropleth(count_data, geojson=Toronto_fsa, locations='CFSAUID',       
                            color=outcome_,
                            color_continuous_scale="viridis_r",
                            featureidkey="properties.CFSAUID",
                            projection="mercator",
                          )

    fig1.update_geos(fitbounds="locations", visible=False)
    fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})    
    
    if daily_ == 'TOTAL':
    
        df = data.copy()
        df['Reported Date'] = pd.to_datetime(df['Reported Date'])
        df = df.set_index('Reported Date')
        df['Count'] = 1  
        
        daily_data = pd.DataFrame(df['Count'].resample('D').count()).reset_index()
        
    else:
        
        df = data.copy()
        df = df[df['Outcome']==daily_]
        df['Reported Date'] = pd.to_datetime(df['Reported Date'])
        df = df.set_index('Reported Date')
        df['Count'] = 1  
        
        daily_data = pd.DataFrame(df['Count'].resample('D').count()).reset_index()
        
    fig2 = px.line(daily_data, x='Reported Date',y='Count',template="simple_white")

    fig2.update_yaxes(title_text="Total Cases")
    fig2.update_xaxes(title_text="Date reported")
    
    
    if agegroup_ == 'ALL':
        df3 = data.copy()
        source_data = df3.groupby('Source of Infection').size().reset_index(name='Count')
        source_data.rename(columns={'Source of Infection':'Source'},inplace=True)
        source_data = source_data.query('Source != "Pending"')
        source_data['Source'] = source_data['Source'].replace({'N/A - Outbreak associated':'Outbreak','Unknown/Missing':'Unknown'})
        
    else:
        df3 = data.copy()
        df3 = df3[df3['Age Group']==agegroup_]
        source_data = df3.groupby('Source of Infection').size().reset_index(name='Count')
        source_data.rename(columns={'Source of Infection':'Source'},inplace=True)
        source_data = source_data.query('Source != "Pending"')
        source_data['Source'] = source_data['Source'].replace({'N/A - Outbreak associated':'Outbreak','Unknown/Missing':'Unknown'})
            
    fig3 = px.bar(source_data.query('Source != "Unknown"'), x='Source', y='Count',color = "Count"
             ,color_continuous_scale = 'sunsetdark',text='Count',template="simple_white")

    fig3.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig3.update_yaxes(title_text="Total Cases")
    fig3.update_xaxes(title_text="Source of Infection")
    
    
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])

    fig4.add_trace(
        go.Bar(x=Age_data['Age_Group'], y=Age_data['Total_Count'], name="Covid Cases Count",marker=dict(
            color=Age_data['Total_Count'],
            colorscale="burg"
        ),text=Age_data['Total_Count']),
        secondary_y=False,
    )
    
    fig4.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    
    fig4.add_trace(
        go.Scatter(x=Age_data['Age_Group'], y=Age_data['Count_fatal'], name="Number of fatal cases",
                   line = dict(color='black', width=2)),
        secondary_y=True,
    )
    
    fig4.update_yaxes(title_text="Total Cases", secondary_y=False)
    fig4.update_yaxes(title_text="Fatal Cases", secondary_y=True)
    fig4.update_xaxes(title_text="Age Group")
    
    fig4.update_layout(template="simple_white")
    
    return string1,string2,string3,string4,string5,fig1,fig2,fig3,fig4
    
    

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
