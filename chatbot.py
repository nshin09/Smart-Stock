import yfinance as yf
from openai import OpenAI
import os
from dotenv import load_dotenv
from stock import fetch_stock_data

load_dotenv()
client = OpenAI(base_url="https://api.aimlapi.com/v1", api_key= os.getenv("OPENAI_API_KEY"))

def generate_summary(tickers, period):
    summaries = {}
    for ticker in tickers:
        hist = fetch_stock_data(ticker,period)
        if hist.empty or "Close" not in hist:
            continue
        first = str(round(hist["Close"].iloc[0],2)) if not hist["Close"].empty else "N/A"
        last = str(round(hist["Close"].iloc[-1],2)) if not hist["Close"].empty else "N/A"
        percent_change = str(round(((float(last) / float(first)) - 1) * 100,2)) if first and last else "N/A"

        high = str(round(hist["High"].max(),2)) if "High" in hist else "N/A"
        low = str(round(hist["Low"].min(),2)) if "Low" in hist else "N/A"
        avg = str(round(hist["Close"].mean(),2)) if "Close" in hist else "N/A"
        vol = str(round(hist["Close"].std(),2)) if "Close" in hist else "N/A"

        summaries[ticker] = f"{ticker}: first = {first}, last = {last}, % change = {percent_change}, high = {high}, low = {low}, average = {avg}, volatility = {vol}\n"        
    try :
        response = client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",  # any model that you have access to "gpt-4o-mini", 
            messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": f"Here are the stats for each ticker in the last {period}: {summaries}. "
            "Please give a clear and concise summary. If a field is not applicable, try your"
            " best to give a good summary"}])
    except Exception as e:
        print(f"error: {e}") # debug
        return "Analyst limit has been reached for today. Please come back tommorrow"
    return response.choices[0].message.content.strip()