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


def plot_data(ticker, name, hist, period):
    fig = go.Figure()
    
    # Ensure index is datetime
    if not hist.index.dtype.kind in 'M':
        hist.index = pd.to_datetime(hist.index)

    # Create equal-spacing x values
    x_equal = list(range(len(hist)))
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
    # Decide whether to show markers
    num_points = len(hist)
    mode = "lines+markers" if num_points <= 100 else "lines"

    # Choose hover template
    hover_format = "Date: %{customdata}<br>Price: $%{y:.2f}<extra></extra>"

    # Plot with equal spacing
    fig.add_trace(go.Scatter(
        x=x_equal,
        y=hist["Close"],
        mode=mode,
        name="Closing Price",
        customdata=dates,  # real date labels for hover
        hovertemplate=hover_format
    ))

    # Pick fewer ticks so labels don’t overlap
    step = max(1, len(x_equal) // 10)  
    tickvals = x_equal[::step]
    ticktext = [tick[i] for i in tickvals]

    fig.update_layout(
        title=f"{name} ({ticker.upper()}) - Last {period}",
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
    # fig = go.Figure()
    
    # # Ensure index is datetime
    # if not hist.index.dtype.kind in 'M':
    #     hist.index = pd.to_datetime(hist.index)
    # x_equal = list(range(len(hist)))
    # # Decide whether to show markers
    # num_points = len(hist)
    # mode = "lines+markers" if num_points <= 100 else "lines"
    # dates = hist.index.strftime("%Y-%m-%d %H:%M")
    # # Determine hover format and x-axis tick format
    # if period in "1d":  # intraday
    #     tick_format = "%H:%M"
    #     hover_format = "Time: %{x|%H:%M}<br>Price: $%{y:.2f}<extra></extra>"
    # elif period in "5d":
    #     tick_format = "%d %H:%M"
    #     hover_format = "Date: %{x|%d %H %M}<br>Price: $%{y:.2f}<extra></extra>"
    # elif period in ["2wk", "1mo"]:
    #     tick_format = "%b %d"
    #     hover_format = "Date: %{x|%b %d}<br>Price: $%{y:.2f}<extra></extra>"
    # else:  # longer periods
    #     tick_format = "%Y-%m-%d"
    #     hover_format = "Date: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>"

    # fig.add_trace(go.Scatter(
    #     x=x_equal,
    #     y=hist["Close"],
    #     mode=mode,
    #     name="Closing Price",
    #     customdata=dates,
    #     hovertemplate=hover_format
    # ))

    # fig.update_layout(
    #     title=f"{name} ({ticker.upper()}) - Last {period}",
    #     xaxis_title="Date/Time",
    #     yaxis_title="Price ($)",
    #     template="plotly_white",
    #     xaxis=dict(
    #         showspikes=True,
    #         spikemode="across",
    #         tickformat=tick_format
    #     )
    # )

    # return fig.to_html(full_html=False)
    



def is_stock_valid(stock):
    try:
        # Attempt to access a key piece of information.
        # This will raise an exception if the ticker is invalid.
        _ = stock.info['symbol']
        _ = stock.info['longName']
        return True
    except Exception:
        # If an exception occurs, the ticker is not valid.
        return False
    