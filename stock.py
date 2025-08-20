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
    
    hist = yf.Ticker(ticker).history(period=period, interval=interval, prepost=True)
    return hist


def plot_data(tickers, period):
    fig = go.Figure()
    # Decide whether to show markers
    # Choose hover template
    hover_format = "Date: %{customdata}<br>Price: $%{y:.2f}<extra></extra>"

    # Ensure index is datetime
    for ticker in tickers:
        hist = fetch_stock_data(ticker,period)
        if hist.empty:
            continue
               # Create equal-spacing x values
        if period in "1d":  # intraday
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
        num_points = len(hist)
        mode = "lines+markers" if num_points <= 100 else "lines"

        fig.add_trace(go.Scatter(
        x=x_equal,
        y=hist["Close"],
        mode=mode,
        name= f"{name}, ({ticker.upper()})",
        customdata=dates,  # real date labels for hover
        hovertemplate=hover_format
    ))

    # Plot with equal spacing
    # fig.add_trace(go.Scatter(
    #     x=x_equal,
    #     y=hist["Close"],
    #     mode=mode,
    #     name="Closing Price",
    #     customdata=dates,  # real date labels for hover
    #     hovertemplate=hover_format
    # ))
    # Pick fewer ticks so labels don’t overlap
    step = max(1, len(x_equal) // 10)  
    tickvals = x_equal[::step]
    ticktext = [tick[i] for i in tickvals]
    title = None
    if len(tickers) > 1:
        ticker_list_str = ", ".join(tickers)
        title = f"{ticker_list_str.upper()} - Last {period}"
    else:
        title = f"{name} ({ticker.upper()}) - Last {period}"

    fig.update_layout(
        title= title,
        xaxis_title="Date",
        yaxis_title="Price ($)",
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
    



def is_ticker_valid(ticker):
    try:
        # Attempt to access a key piece of information.
        # This will raise an exception if the ticker is invalid.
        stock = yf.Ticker(ticker)
        _ = stock.info['symbol']
        _ = stock.info['longName']
        return True
    except Exception:
        # If an exception occurs, the ticker is not valid.
        return False
    