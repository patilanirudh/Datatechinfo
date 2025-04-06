# import dash
# from dash import dcc,html #dash core components
# from dash.dependencies import Input,Output
# import numpy as np
# import plotly.express as px

# #initializes the app
# app=dash.Dash(__name__)

# app.layout=html.Div([
#     html.H1("First Dash APP"), #app title 
#     dcc.Input(id='num',type="number",value=1), #no input box
#     html.Div(id="output"), #placeholder for o/p
#     dcc.Graph(id="plot") #placeholder for graph

# ])

# @app.callback(
#     [Output("output","children"),Output("plot","figure")],
#     [Input("num","value")]
# )
# def update(num):
#     sq=num**2 if num else 0 #calculates square
#     x=np.linspace(0,num,100) #creates data points from 0-num
#     y=x**2
#     fig=px.line(x=x,y=y,labels={'x':"input","y":"o/p"}) #plots graph
#     return f" squared o/p: {sq}",fig #returns text and graph

# if __name__=='__main__':
#     app.run(debug=True) #starts the server

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np

# Initialize Dash app
app = Dash(__name__)
app.title = "Personal Finance Tracker (INR)"

app.layout = html.Div([
    html.H1("💰 Personal Finance Tracker (INR)", style={'textAlign': 'center'}),
    html.Hr(),
    
    html.Div([
        html.Div([
            html.H3("Enter Your Monthly Income & Expenses"),
            dcc.Input(id='income', type='number', placeholder="Your Total Monthly Income (₹)", step=0.01),
            dcc.Input(id='rent', type='number', placeholder="Rent (₹)", step=0.01),
            dcc.Input(id='food', type='number', placeholder="Food Expenses (₹)", step=0.01),
            dcc.Input(id='travel', type='number', placeholder="Travel Expenses (₹)", step=0.01),
            dcc.Input(id='other', type='number', placeholder="Other Expenses (₹)", step=0.01),
            html.Button("💡 Calculate Insights", id='calculate', n_clicks=0)
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("📈 Financial Summary"),
            html.Div(id='summary-output')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
    
    html.Hr(),
    html.Div([
        dcc.Graph(id='expense-pie-chart'),
        dcc.Graph(id='income-expense-bar-chart'),
        dcc.Graph(id='savings-projection-chart')
    ])
])

@app.callback(
    [Output('summary-output', 'children'),
     Output('expense-pie-chart', 'figure'),
     Output('income-expense-bar-chart', 'figure'),
     Output('savings-projection-chart', 'figure')],
    [Input('calculate', 'n_clicks')],
    [Input('income', 'value'), Input('rent', 'value'), Input('food', 'value'),
     Input('travel', 'value'), Input('other', 'value')]
)
def update_finance(n_clicks, income, rent, food, travel, other):
    if not all([income, rent, food, travel, other]):
        return "Enter all values to see insights", {}, {}, {}
    
    total_expense = rent + food + travel + other
    savings = income - total_expense
    
    summary = html.Div([
        html.P(f"Total Expenses: ₹{total_expense:.2f}"),
        html.P(f"Savings: ₹{savings:.2f}", style={'color': 'green' if savings > 0 else 'red'})
    ])
    
    expense_labels = ["Rent", "Food", "Travel", "Other"]
    expense_values = [rent, food, travel, other]
    fig_pie = px.pie(names=expense_labels, values=expense_values, title="Expense Distribution", hole=0.3)
    
    categories = ["Income", "Expenses"]
    values = [income, total_expense]
    fig_bar = px.bar(x=categories, y=values, title="Income vs. Expenses", labels={"x": "Category", "y": "Amount (₹)"}, color=categories)
    
    months = np.arange(1, 13)
    future_savings = np.cumsum([savings] * 12)
    fig_line = px.line(x=months, y=future_savings, labels={"x": "Months", "y": "Projected Savings (₹)"}, title="Projected Savings for Next 12 Months", markers=True)
    fig_line.update_traces(marker=dict(color='darkblue'))
    for i, value in enumerate(future_savings):
        fig_line.add_annotation(x=months[i], y=value, text=f"₹{value:.2f}", showarrow=True, arrowhead=2, font=dict(color="darkblue"))
    
    return summary, fig_pie, fig_bar, fig_line

if __name__ == '__main__':
    app.run(debug=True)