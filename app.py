import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

#Problem 2
gss_clean_display = gss_clean.groupby('sex').agg({'income':'mean', 'job_prestige':'mean','socioeconomic_index':'mean','education':'mean'}).reset_index()
gss_clean_display = round(gss_clean_display, 2)
gss_clean_display = gss_clean_display.rename({'sex':'Sex', 'income':'Mean Income',
                                   'job_prestige':'Mean Occupational Prestige',
                                   'socioeconomic_index':'Mean Socioeconomic Index',
                                   'education':'Mean Years of Education'}, axis=1)
table = ff.create_table(gss_clean_display)

#Problem 4
figscatter = px.scatter(gss_clean, x='job_prestige', y='income', trendline='ols',
                 color = 'sex', 
                 height=600, width=600,
                 labels={'job_prestige':'Occupation Prestige Score', 
                        'income':'Annual Income'},
                 hover_data=['education', 'socioeconomic_index'])

#Problem 5
figbox1 = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                   labels={'income':'Annual Income', 'sex':''}, height = 600, width = 600)
figbox1.update_layout(showlegend=False)

figbox2 = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                   labels={'job_prestige':'Occupation Prestige Score', 'sex':''}, height = 600, width = 600)
figbox2.update_layout(showlegend=False)

#Problem 6
newData = gss_clean[['income','sex','job_prestige']]
newData['job_prestige_group'] = pd.cut(newData['job_prestige'], bins=6)
newData.dropna(inplace=True)
figFacet = px.box(newData, x='sex', y='income', color='sex', 
             facet_col='job_prestige_group', facet_col_wrap=2,
            labels={'job_prestige':'Occupation Prestige Score', 'sex':''},
            width=1000, height=1000)
figFacet.update_layout(showlegend=False)

#Problem 3 and Dashboard
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

xChoices = ['satjob','relationship','male_breadwinner','men_bettersuited','child_suffer','men_overwork']
groupChoices = ['sex','region','education']

app.layout = html.Div(
    [
        html.H1("Exploring Gender Differences through GSS Data"),
        
        #dcc.Markdown(children = markdown_text),
        
        html.H3("Comparing Male vs. Female for Average Income, Education, Occupational Prestige, and Socioeconomic Index"),
        
        dcc.Graph(figure=table),
        
        html.H3("Relationship between Annual Income and Occupation Prestige Score across Genders"),
        
        dcc.Graph(figure=figscatter),
        
        html.Div([
            
            html.H3("Distribution of Annual Income by Sex"),
            
            dcc.Graph(figure=figbox1)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H3("Distribution of Job Prestige Score by Sex"),
            
            dcc.Graph(figure=figbox2)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H3("Distribution of Annual Income by Sex Per Job Prestige Score Bracket"),
        
        dcc.Graph(figure=figFacet),
        
        html.H3("Counts of Levels of Agreement to Survey Questions"),
        
        html.Div([

            html.H4("X-Axis Category"),

            dcc.Dropdown(id='x-axis',
                options=[{'label': i, 'value': i} for i in xChoices],
                value='male_breadwinner'),

            html.H4("Group-by Category"),

            dcc.Dropdown(id='group-by',
                options=[{'label': i, 'value': i} for i in groupChoices],
                value='sex'),

        ], style={'width': '25%', 'float': 'left'}),
        
        html.Div([
            
            dcc.Graph(id="graph")
        
        ], style={'width': '75%', 'float': 'right'}),
    ]
)
@app.callback(Output(component_id="graph",component_property="figure"), 
                  [Input(component_id='x-axis',component_property="value"),
                   Input(component_id='group-by',component_property="value")])

def make_figure(x, color):
    gss_bar = gss_clean.groupby([color, x]).size().reset_index()
    gss_bar = gss_bar.rename({0:'Count'}, axis=1)
    return px.bar(
        gss_bar,
        x=x,
        y='Count',
        color=color,
        barmode='group',
        hover_data=[color],
        width=1000,
        height=600,
)

if __name__ == '__main__':
    app.run_server(debug=True)
