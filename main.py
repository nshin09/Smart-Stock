from openai import OpenAI
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
from waitress import serve
import yfinance as yf

from stock import plot_data, fetch_stock_data
from chatbot import generate_summary
load_dotenv()
app = Flask(__name__)

news_api_key = os.getenv("NEWS_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    try:
        if request.method == "POST":
            results = request.form.getlist("tickers")
            period = request.form.get("period", "1y")
            mode = request.form.get("mode")
            data = None
            tickers = []
            if results:
                for i in range(0,len(results)):
                    results[i] = results[i].strip()
                    result = yf.Search(results[i])
                    if result.quotes:
                        data = result.quotes[0]
                        if not fetch_stock_data(data['symbol'], "1y").empty and data['symbol'] not in tickers:
                            tickers.append(data['symbol'])
            if tickers:
                prices = []
                company_names = []
                for tick in tickers:
                    stock = yf.Ticker(tick)
                    try:
                        prices.append(str(round(stock.history(period="1d")["Close"].iloc[-1], 2)))
                    except Exception as e:
                        try:
                            prices.append(str(round(stock.history(period="1wk")["Close"].iloc[-1], 2)))
                        except Exception as e:
                            prices.append("N/A")
                    try:
                        company_names.append(stock.info['longName'])
                    except Exception as e:
                        try:
                            company_names.append(stock.info['shortName'])
                        except Exception as e:
                            company_names.append("null")
                    
                price = ", $".join(prices)
                company_name = ", ".join(company_names)
                ticker = ", ".join(tickers)                                 
            # Creating the plot
                graph_JSON = plot_data(tickers, period, mode)
                return render_template("index.html", price = price, company_name = company_name, ticker = ticker, graph_JSON = graph_JSON, period = period, tickers = results, mode = mode)
        return render_template("index.html", company_name = "No Results Found")
    except Exception as e:
        return render_template("index.html", company_name = f"Error loading search: {e} Please try again later.")



# @app.route('/index', methods=['GET', 'POST'])
@app.route("/search_tickers", methods=['GET', 'POST'])
def search_tickers():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    try:
        result = yf.Search(query)  # new yfinance method
        if not result.quotes:
            return jsonify([])

        # Extract only symbol + shortname
        tickers = []
        for q in result.quotes[:10]:  # top 10 matches
            try:
                name = f"{q['longname']}, ({q['symbol']})"
                if name not in tickers:
                    tickers.append(f"{q['longname']}, ({q['symbol']})")
            except Exception as e:
                try: 
                    name = f"{q['shortname']}, ({q['symbol']})"
                    if name not in tickers:
                        tickers.append(f"{q['shortname']}, ({q['symbol']})")
                except Exception as e:
                    continue
        return jsonify(tickers)

    except Exception as e:
        print("System error:", e)
        return jsonify([])

@app.route('/api/question', methods=['GET', 'POST'])
def get_question():
    if request.method == 'POST':
        results = request.form.getlist("tickers")
        period = request.form.get("period", "1y")
        tickers = []
        if results:
            for i in range(0,len(results)):
                results[i] = results[i].strip()
                result = yf.Search(results[i])
                if result.quotes:
                    data = result.quotes[0]
                    if not fetch_stock_data(data['symbol'], "1y").empty and data['symbol'] not in tickers:
                        tickers.append(data['symbol'])
            response = generate_summary(tickers, period)
            if response:
                return jsonify({"reply": response})
            else:
                return jsonify({"reply": "Cannot generate summary at this time. Please try again later."})
    return jsonify({"reply": "Please enter at least one valid ticker"})
    



if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000) #http://127.0.0.1:8000/




