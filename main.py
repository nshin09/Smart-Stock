from openai import OpenAI
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
from waitress import serve
import yfinance as yf

from stock import plot_data, is_ticker_valid, fetch_stock_data


load_dotenv()
app = Flask(__name__)
client = OpenAI(base_url="https://api.aimlapi.com/v1", api_key= os.getenv("OPENAI_API_KEY"))
news_api_key = os.getenv("NEWS_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        results = request.form.get("search").split(',')
        period = request.form.get("period", "1y")
        data = None
        tickers = []
        if results:
            for i in range(0,len(results)):
                results[i] = results[i].strip()
                result = yf.Search(results[i])
                if result.quotes:
                    data = result.quotes[0]
                    if is_ticker_valid(data['symbol']):
                        tickers.append(data['symbol'])
           # stock = yf.Ticker(ticker)
                #price = round(stock.history(period="1d")["Close"].iloc[-1], 2)
                #company_name = stock.info['longName']
               # hist = fetch_stock_data(ticker, period)
        if tickers:
            prices = []
            company_names = []
            for tick in tickers:
                stock = yf.Ticker(tick)
                prices.append(str(round(stock.history(period="1d")["Close"].iloc[-1], 2)))
                company_names.append(stock.info['longName'])
            price = ", $".join(prices)
            company_name = ", ".join(company_names)
            ticker = ", ".join(tickers)                                 
        # Creating the plot
            graph_JSON = plot_data(tickers, period)
            return render_template("index.html", price = price, company_name = company_name, ticker = ticker, graph_JSON = graph_JSON, period = period)
    return render_template("index.html")


# @app.route('/index', methods=['GET', 'POST'])


@app.route('/api/question', methods=['GET', 'POST'])
def get_question():
    if request.method == 'POST':
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        #prompt = request.form.get('prompt')
        if prompt:
            reply = chat_with_gpt(prompt)
            #print(reply) this is for debugging 
            return jsonify({"reply": reply})
            #return render_template("question.html", reply = reply)
        else:
            return jsonify({"reply": ""}), 400
    else:
        return render_template("index.html")
    
def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-4 if your key allows
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000) #http://127.0.0.1:8000/





    # print("AIML ChatGPT (type 'quit' to exit)")
    # while True:
    #     user_input = input("You: ")
    #     if user_input.lower() in ["quit", "exit"]:
    #         break
    #     reply = chat_with_gpt(user_input)
    #     print("Bot:", reply)