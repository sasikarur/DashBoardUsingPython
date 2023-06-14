import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

df = pd.read_csv('C:\\Users\\sasikumarchennova\\Documents\\Data Science\\Excel\\Data\\telcom.csv')

app = dash.Dash()

labels = df.columns

def univariate(df, row):
    table = df.groupby([row]).size().reset_index()
    table.columns = [row, 'Counts']
    table['percentage'] = table['Counts'] / sum(table['Counts']) * 100
    table['Percent'] = round(table['percentage'], 1).astype(str) + '%'
    return table

def univariate_charts(table, row):
    fig = px.bar(table, x=row, y=['percentage'], text=table['Percent'], title="Region")
    fig.update_layout(template='plotly_white', title_x=0.5)
    fig.show()

def univariate_piechart(table, row):
    fig = px.pie(table, values='Counts', names=row, title="Region")
    fig.update_layout(template='seaborn', title_x=0.5)
    fig.show()

def bivariate_table(df, row, column):
    table = df.groupby([row, column]).size().reset_index()
    table['percentage'] = df.groupby([row, column]).size().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values.round(1)
    table.columns = [row, column, 'Counts', 'percentage']
    table['Percent'] = round(table['percentage'], 1).astype(str) + '%'
    return table

def bivariate_chart(table, row, column):
    fig = px.bar(table, x=row, y=['percentage'], color=column, text=table['Percent'], title=str(row).upper() + " Vs. " + str(column).upper() + " CHART")
    fig.update_layout(template='plotly_white', title_x=0.5)
    fig.show()

def bivariate_piechart(table, row, column):
    yes_df = table[table[column] == 'Yes']
    fig_yes = px.pie(yes_df, values='Counts', names=row, title='Churn Vs  {} (Yes)'.format(row))
    fig_yes.update_traces(textposition='inside', textinfo='percent+label')
    fig_yes.update_layout(title_x=0.5)

    no_df = table[table[column] == 'No']
    fig_no = px.pie(no_df, values='Counts', names=row, title='Churn Vs  {} (No)'.format(row))
    fig_no.update_traces(textposition='inside', textinfo='percent+label')
    fig_no.update_layout(title_x=0.5)

    return fig_yes, fig_no

table_type = ['Univariate','Bivariate']

app.layout = html.Div([
    html.Div("Telecommunication Analysis Report", style={'color': 'red', 'fontSize': 40, 'textAlign': 'center'}),
    html.P("Select your variable:"),
    dcc.Dropdown(id='dropdown1', options=[{'label': label, 'value': label} for label in labels[1:-1]], value=labels[1]),
    dcc.Dropdown(id='dropdown2', options=['Univariate','Bivariate'], value='Univariate'),
    html.Br(),
    dcc.RadioItems(
        options=[{'label': 'Bar', 'value': 'Bar'}, {'label': 'Pie', 'value': 'Pie'}],
        value='Bar',
        id='chart-type',
        inline=True
    ),
    dcc.Graph(id='graph1')
], style={'width': '95%', 'display': 'inline-block'})

@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown1', 'value'), 
     Input('dropdown2', 'value'), 
     Input('chart-type', 'value')]
)

def call_back_function(variable, type, chart_type):
    print(variable, type, chart_type)
    if type == 'Univariate':
        if chart_type == 'Bar':
            table = univariate(df, variable)
            fig = px.bar(table, x=variable, y=['percentage'], text=table['Percent'], title=variable + " Bar Chart")
            fig.update_layout(template='plotly_white', title_x=0.5)
            return fig
        else:
            table = univariate(df, variable)
            fig = px.pie(table, values='Counts', names=variable, title=variable + " Pie Chart")
            fig.update_layout(template='seaborn', title_x=0.5)
            return fig
    else:
        if chart_type == 'Bar':
            table = bivariate_table(df, variable, 'churn')
            fig = px.bar(table, x=variable, y=['percentage'], color='churn', text=table['Percent'], title=str(variable).upper() + " Vs. " + str('churn').upper() + " CHART")
            fig.update_layout(template='plotly_white', title_x=0.5)
            return fig
        else:
            table1 = bivariate_table(df, variable, 'churn')
            yes_df = table1[table1['churn'] == 'Yes']
            fig_yes = px.pie(yes_df, values='Counts', names=variable, title='Churn Vs  {} (Yes)'.format(variable))
            fig_yes.update_traces(textposition='inside', textinfo='percent+label')
            fig_yes.update_layout(title_x=0.5)

            table2 = bivariate_table(df, variable, 'churn')
            no_df = table2[table2['churn'] == 'No']
            fig_no = px.pie(no_df, values='Counts', names=variable, title='Churn Vs  {} (No)'.format(variable))
            fig_no.update_traces(textposition='inside', textinfo='percent+label')
            fig_no.update_layout(title_x=0.5)

            fig = make_subplots(rows=1, cols=2, specs=[[{"type": "Pie"}, {"type": "Pie"}]])

            fig.add_trace(go.Pie(values=yes_df['Counts'], labels=yes_df[variable], domain=dict(x=[0, 0.5]), name="Yes"), row=1, col=1)
            fig.add_trace(go.Pie(values=no_df['Counts'], labels=no_df[variable], domain=dict(x=[0.5, 1]), name="No"), row=1, col=2)

            fig.update_layout(
                title_text="Churn Vs. {} Pie Charts".format(variable),
                title_x=0.5
            )

            fig.update_layout(
                annotations=[
                    dict(
                        text="Churn Vs. {} (Yes)".format(variable),
                        x=0.400,
                        y=0.10,
                        font=dict(size=14),
                        showarrow=False
                    ),
                    dict(
                        text="Churn Vs. {} (No)".format(variable),
                        x=1.01,
                        y=0.10,
                        font=dict(size=14),
                        showarrow=False
                    )
                ]
            )

            return fig


if __name__ == '__main__':
    app.run_server(debug=True)
