# Imports 
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import webbrowser

# Download data
tickers = ["BMO.TO", "TD.TO", "RY.TO", "CM.TO", "BNS.TO"]
bankData = yf.download(tickers, period="5y")['Close']

# Calculate returns
dailyReturns = bankData.pct_change()
cumulativeReturns = (1 + dailyReturns).cumprod()
rollingVolatility = dailyReturns.rolling(window=30).std().dropna()

# Colors and labels
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

# Initialize Dash app
app = Dash(__name__)

# Layout
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

    html.Label("Show Monte Carlo Forecast"),
    dcc.Checklist(
        id='forecastToggle',
        options=[{'label': 'Forecast', 'value': 'showForecast'}],
        value=[]
    ),

    dcc.Graph(id='bankGraph')
])

def monteCarloForecast(bank, lastPrice, meanReturn, stdReturn):
    nDays=60
    nSim=1000
    
    simPrices = np.zeros((nDays, nSim))
    for i in range (nSim):
        price = lastPrice
        for j in range (nDays):
            price = price * (1+ np.random.normal(meanReturn, stdReturn))
            simPrices[j, i] = price
    lower = np.percentile(simPrices, 5, axis=1)
    upper = np.percentile(simPrices, 95, axis=1)
    median = np.percentile(simPrices, 50, axis=1)
    futureDates = pd.date_range(start=bankData.index[-1] + pd.Timedelta(days=1), periods=nDays, freq='B')
    return futureDates, median, lower, upper

# Callback to update graph
@app.callback(
    Output('bankGraph', 'figure'),
    Input('bankDropdown', 'value'),
    Input('metricDropdown', 'value'),
    Input('forecastToggle', 'value')
)

def updateGraph(selectedBank, selectedMetric, forecastToggle):
    fig = go.Figure()

    # Determine metric to plot
    if selectedMetric == 'cumulativeReturns':
        dataToPlot = cumulativeReturns
        yLabel = "Cumulative Return ($1 Invested)"
    elif selectedMetric == 'dailyReturns':
        dataToPlot = dailyReturns
        yLabel = "Daily Return"
    elif selectedMetric == 'rollingVolatility':
        dataToPlot = rollingVolatility
        yLabel = "Volatility (Std Dev of Daily Returns)"

    # Plot historical data
    banksToPlot = dataToPlot.columns if selectedBank == 'All' else [selectedBank]
    for bank in banksToPlot:
        fig.add_trace(go.Scatter(
            x=dataToPlot.index,
            y=dataToPlot[bank],
            mode='lines',
            name=labels[bank],
            line=dict(color=colors[bank], width=2)
        ))

    # Add forecast if selected
    if 'showForecast' in forecastToggle and selectedBank != 'All' and selectedMetric == 'cumulativeReturns':
        lastPrice = cumulativeReturns[selectedBank].iloc[-1]
        meanReturn = dailyReturns[selectedBank].mean()
        stdReturn = dailyReturns[selectedBank].std()
        
        futureDates, median, lower, upper = monteCarloForecast(selectedBank, lastPrice, meanReturn, stdReturn)


        # Median forecast
        fig.add_trace(go.Scatter(
            x=futureDates,
            y=median,
            mode='lines',
            name=f"{labels[selectedBank]} Forecast Median",
            line=dict(color=colors[selectedBank], width=2, dash='dash')
        ))
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=np.concatenate([futureDates, futureDates[::-1]]),
            y=np.concatenate([upper, lower[::-1]]),
            fill='toself',
            fillcolor='rgba(0,0,0,0.1)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=True,
            name=f"{labels[selectedBank]} 5-95% Forecast"
        ))

    fig.update_layout(
        title=f"{selectedMetric.replace('daily', 'Daily').replace('cumulative', 'Cumulative').replace('Returns',' Returns').replace('Volatility',' Volatility')} of Selected Banks",
        xaxis_title="Date",
        yaxis_title=yLabel,
        hovermode="x unified",
        legend_title="Bank",
        template="plotly_white"
    )

    return fig

# Run app
if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:8050/")
    app.run(debug=True, host='127.0.0.1', port=8050)