# interactiveBankAnalysis.py
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import webbrowser

# 1. Download data
tickers = ["BMO.TO", "TD.TO", "RY.TO", "CM.TO", "BNS.TO"]
bankData = yf.download(tickers, period="5y")['Close']

# 2. Calculate returns
dailyReturns = bankData.pct_change()
cumulativeReturns = (1 + dailyReturns).cumprod()
rollingVolatility = dailyReturns.rolling(window=30).std().dropna()

# 3. Colors and labels
colors = {
    "BMO.TO": "blue",
    "TD.TO": "green",
    "RY.TO": "gold",
    "CM.TO": "red",
    "BNS.TO": "pink"
}

labels = {
    "BMO.TO": "BMO",
    "TD.TO": "TD",
    "RY.TO": "RBC",
    "CM.TO": "CIBC",
    "BNS.TO": "Scotiabank"
}

# 4. Initialize Dash app
app = Dash(__name__)

# 5. Layout
app.layout = html.Div([
    html.H1("Interactive Analysis of 5 Major Canadian Banks"),

    html.Label("Select Bank:"),
    dcc.Dropdown(
        id='bankDropdown',
        options=[{'label': labels[t], 'value': t} for t in tickers] + [{'label': 'All Banks', 'value': 'All'}],
        value='All'
    ),

    html.Label("Select Metric:"),
    dcc.Dropdown(
        id='metricDropdown',
        options=[
            {'label': 'Cumulative Returns', 'value': 'cumulativeReturns'},
            {'label': 'Daily Returns', 'value': 'dailyReturns'},
            {'label': 'Rolling Volatility', 'value': 'rollingVolatility'}
        ],
        value='cumulativeReturns'
    ),

    dcc.Graph(id='bankGraph')
])

# 6. Callback to update graph
@app.callback(
    Output('bankGraph', 'figure'),
    Input('bankDropdown', 'value'),
    Input('metricDropdown', 'value')
)
def updateGraph(selectedBank, selectedMetric):
    if selectedMetric == 'cumulativeReturns':
        dataToPlot = cumulativeReturns
        yLabel = "Cumulative Return ($1 Invested)"
    elif selectedMetric == 'dailyReturns':
        dataToPlot = dailyReturns
        yLabel = "Daily Return"
    elif selectedMetric == 'rollingVolatility':
        dataToPlot = rollingVolatility
        yLabel = "Volatility (Std Dev of Daily Returns)"

    fig = go.Figure()

    if selectedBank == 'All':
        for bank in dataToPlot.columns:
            fig.add_trace(go.Scatter(
                x=dataToPlot.index,
                y=dataToPlot[bank],
                mode='lines',
                name=labels[bank],
                line=dict(color=colors[bank], width=2)
            ))
    else:
        fig.add_trace(go.Scatter(
            x=dataToPlot.index,
            y=dataToPlot[selectedBank],
            mode='lines',
            name=labels[selectedBank],
            line=dict(color=colors[selectedBank], width=2)
        ))

    fig.update_layout(
        title=f"{selectedMetric.replace('Returns',' Returns').replace('Volatility',' Volatility')} of Selected Banks",
        xaxis_title="Date",
        yaxis_title=yLabel,
        hovermode="x unified",
        legend_title="Bank",
        template="plotly_white"
    )

    return fig

# 7. Run app
if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:8050/")
    app.run(debug=True, host='127.0.0.1', port=8050)