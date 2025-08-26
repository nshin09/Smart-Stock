import yfinance as yf
from yfinance import search
import plotly.graph_objs as go
import pandas as pd
def fetch_stock_data(ticker, period):
    period = period.lower()
    if period == "1d":
        interval = "1m"
    elif period == "5d":
        interval = "15m"
    elif period == "2wk":
        interval = "30m"
    elif period == "1mo":
        interval = "90m"
    elif period in ["6mo", "1y"]:
        interval = "1d"
    elif period == "5y":
        interval = "1wk"
    elif period == "max":
        interval = "1mo"
    else:
        raise ValueError("Unsupported period")
    try:
        hist = yf.Ticker(ticker).history(period=period, interval=interval, prepost=True)
        return hist
    except Exception:
        return None


def plot_data(tickers, period, mode):
    fig = go.Figure()
    if mode == "percent": 
        hover_format = "Date: %{customdata}<br>Percent: %{y:.2f}%<extra></extra>"
    else:
        hover_format = "Date: %{customdata}<br>Price: $%{y:.2f}<extra></extra>"


    if len(tickers) == 1: # for single tickers we want equal spacing amongst data points, regardless of time intervals. 
        ticker = tickers[0]
        
        hist = fetch_stock_data(tickers[0],period)
        if hist.empty:
            return None
        if period in "1d": 
            tick = hist.index.strftime("%H:%M")
        elif period in "5d":
            tick = hist.index.strftime("%d %H:%M")
        elif period in ["2wk", "1mo", "6mo"]:
            tick = hist.index.strftime("%m-%d")
        else:  # longer periods
            tick = hist.index.strftime("%Y-%m")
        
        if period in ["1d","5d","2wk", "1mo"]:
            dates = hist.index.strftime("%Y-%m-%d %H:%M") 
        else:  # formatted dates for labels
            dates = hist.index.strftime("%Y-%m-%d") 
        if not hist.index.dtype.kind in 'M':
            hist.index = pd.to_datetime(hist.index)
        x_equal = list(range(len(hist)))
        name = yf.Ticker(ticker).info.get("longName", ticker)
        values = None
        if mode == "percent":
            # get the percentage values 
            values = (hist["Close"] / hist["Close"].iloc[0] - 1) * 100
            y_title = "Change (%)"
        else:
            y_title = "Price ($)"
            values = hist["Close"]
        fig.add_trace(go.Scatter(
        x=x_equal,
        y=values,
        mode="lines",
        name= f"{name}, ({ticker.upper()})",
        customdata=dates,  
        hovertemplate=hover_format ))

        step = max(1, len(x_equal) // 10)  
        tickvals = x_equal[::step]
        ticktext = [tick[i] for i in tickvals]
        title = f"{name} ({ticker.upper()}) - Last {period}"

        fig.update_layout(
            width = 1200,
            height = 600,
            title= title,
            xaxis_title="Date",
            yaxis_title= y_title,
            template="plotly_white",
            xaxis=dict(
                tickmode="array",
                tickvals=tickvals,
                ticktext=ticktext,
                showspikes=True,
                spikemode="across"
        )
    )
        return fig.to_html(full_html=False)
    else: # for multiple tickers we want points that line up perfectly with the time ticks
        histories = {}


        for ticker in tickers:
            hist = fetch_stock_data(ticker, period)
            if not hist.empty:
                histories[ticker] = hist

            if not histories:
                return "<p>No data available</p>"
            if period in ["1d","5d","2wk", "1mo"]:
                dates = hist.index.strftime("%Y-%m-%d %H:%M") 
            else:  
                dates = hist.index.strftime("%Y-%m-%d") 
        
        min_end = min(hist.index.max() for hist in histories.values())
        max_start = max(hist.index.min() for hist in histories.values())

  
        for ticker, hist in histories.items():
            hist = hist.loc[(hist.index >= max_start) & (hist.index <= min_end)]
            if hist.empty:
                continue

            name = yf.Ticker(ticker).info.get("longName", ticker)
            if mode == "percent":
            
                values = (hist["Close"] / hist["Close"].iloc[0] - 1) * 100
                y_title = "Change (%)"
            else:
                values = hist["Close"]
                y_title = "Price ($)"
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=values,
                mode= "lines",
                name=f"{name} ({ticker.upper()})",
                hovertemplate= hover_format,
                customdata=dates 
            ))
        fig.update_layout(
            width = 1200,
            height = 600,
            title=f"{', '.join(tickers)} - Last {period}",
            xaxis_title="Date",
            yaxis_title= y_title,
            template="plotly_white",
            xaxis=dict(
                range=[max_start, min_end],  # force common window
                showspikes=True,
                spikemode="across",
                nticks = 10
                
            )
        )
        return fig.to_html(full_html=False)
   
 
    


