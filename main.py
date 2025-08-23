# Import Libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Download 5 years of historical data
ticker = "BMO.TO"
data = yf.download(ticker, period="5y")

# Calculate daily returns, 30-day moving average, 100-day moving average
data["Daily Return"] = data["Close"].pct_change()
data["MA30"] = data["Close"].rolling(window=30).mean()
data["MA100"] = data["Close"].rolling(window=100).mean()

# Plot stock price with 30-day and 100-day moving average
plt.figure(figsize=(12,6))
plt.plot(data["Close"], label="BMO Stock Price", alpha=0.8)
plt.plot(data["MA30"], label="30-Day MA", linestyle="--")
plt.plot(data["MA100"], label="100-Day MA", linestyle="--")

# Add title, labels, and legend
plt.title("BMO Stock Price with Moving Averages (5 Years)")
plt.xlabel("Date")
plt.ylabel("Price (CAD)")
plt.legend()
plt.show()

# Plot histogram and daily returns to visualize frequency of gains/losses and volatility
plt.figure(figsize=(8,5))
data["Daily Return"].hist(bins=50)

# Add titles and labels
plt.title("BMO Daily Returns Distribution")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.show()

