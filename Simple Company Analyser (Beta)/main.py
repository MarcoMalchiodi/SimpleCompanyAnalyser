import yfinance as yf
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import requests
from flask import request

MY_KEY = 'Your Key'
endpoint = 'https://newsapi.org/v2/everything'

N_ARTICLES = 10

pd.set_option('display.max_rows', None)



def average(my_list):
    count = 0
    total = 0
    for x in my_list:
        total += x
        count += 1
    return (round(float(total/count),2))

def weekly_average(daily_prices, trading_days_per_week=5):
    weekly_averages = []
    
    for i in range(0, len(daily_prices), trading_days_per_week):
        week_prices = daily_prices[i:i+trading_days_per_week]
        if week_prices:  # To handle the last week which might have fewer than 5 trading days
            weekly_avg = round(sum(week_prices) / len(week_prices),2)
            weekly_averages.append(weekly_avg)
    
    return weekly_averages



def chart_maker(my_list):
    formatted_list = []

    for i in range(len(my_list)):
        if i > 0:
            if my_list[i] > my_list[i - 1]:
                formatted_list.append(str(my_list[i]) + " ↑ ")
            elif my_list[i] < my_list[i - 1]:
                formatted_list.append(str(my_list[i]) + " ↓ ")
            else:
                formatted_list.append(str(my_list[i]))
        else:
            formatted_list.append(str(my_list[i]))
    
    return ' '.join(formatted_list)


# ----------------------------- UI ----------------------------- #

from flask import Flask, render_template
    
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyser',methods=["GET","POST"])
def analyser():
    if request.method=="POST":
        company_ticket = request.form['ticket']

        get_data = yf.Ticker(request.form['ticket'])


# ------------------- Analysing Financial Statements ----------- #

# Income Statement (Total Revenue, Gross Profit, Net Income)

        income_statement = get_data.income_stmt
        total_revenue = income_statement.loc[income_statement.index == "Total Revenue"].values.tolist()[0]
        gross_profit = income_statement.loc[income_statement.index == "Gross Profit"].values.tolist()[0]
        net_income = income_statement.loc[income_statement.index == "Net Income"].values.tolist()[0]

# Balance Sheet (Current Assets, Current Liabilities, Total Assets, Total Liabilities, Stockholders Equity)

        balance_sheet = get_data.balance_sheet
        total_assets = balance_sheet.loc[balance_sheet.index == "Total Assets"].values.tolist()[0]
        total_liabilities = balance_sheet.loc[balance_sheet.index == "Total Liabilities Net Minority Interest"].values.tolist()[0]
        current_assets = balance_sheet.loc[balance_sheet.index == "Current Assets"].values.tolist()[0]
        current_liabilities = balance_sheet.loc[balance_sheet.index == "Current Liabilities"].values.tolist()[0]
        stockholders_equity = balance_sheet.loc[balance_sheet.index == "Stockholders Equity"].values.tolist()[0]

# Stock Price at Open
        stock_price = 0
        for key,item in get_data.info.items():
            if key == 'open':
                stock_price = f"{item}"

# Shares Outstanding
        shares_outstanding = 0
        for key,item in get_data.info.items():
            if key == 'sharesOutstanding':
                shares_outstanding = f"{item}"
            
# Preferred Dividends
        


# ------------------------- Indices ------------------- #


# Gross Profit Margin
# Companies with >= 40% tend to have strong competitive advantage.
        gross_profit_margin = []
        for x in range(len(total_revenue)):
            grp_m = gross_profit[x]/total_revenue[x]
            gross_profit_margin.append(round(grp_m, 2))


# Liquidity
# If < 1 is usually bad, but it can be off-set by a greater earning power of competitive companies.
        liquidity = []
        for x in range(len(current_assets)):
            liq = current_assets[x]/current_liabilities[x]
            liquidity.append(round(liq,2))


# ROA
# Usually a higher percentage equals to better prospects, but that's not always the case.
# A company like Coca-Cola has a ROA of about 7%, but her total assets are worth over 40 Bln,
# which makes it harder to take her on, thus granting a competitive advantage.
        roa = []
        for x in range(len(total_assets)):
            ror = net_income[x]/total_assets[x]
            roa.append(round(ror,2))


# Return on Shareholders' Equity
# Anything above 20% is usually a good indicator.
# Note: some companies are so profitable that they don't retain any earnings,
# so they pay them all out to the shareholders.
        updated_net_income = []
        for y in net_income:
            try:
                num = int(y)
                num = float(num)
                updated_net_income.append(num)
            except:
                pass
        return_on_shar_eq = []
        for x in range(len(updated_net_income)):
            shar = updated_net_income[x]/stockholders_equity[x]
            return_on_shar_eq.append(round(shar,2))



# Debt:Shareholders' Equity
# Anything below .80 is usually considered good (the lower, the better). There are exceptions though.
# Banks, for example, have to leverage a lot because of their business.
        debt_to_shareq = []
        for x in range(len(total_liabilities)):
            debt = total_liabilities[x]/stockholders_equity[x]
            debt_to_shareq.append(round(debt,2))

# EPS
# 
        eps = round(net_income[0]/float(shares_outstanding),2)


# P/E Ratio
# Typically, the average P/E ratio is around 20 to 25. 
# Anything below that would be considered a good price-to-earnings ratio, 
# whereas anything above that would be a worse P/E ratio. 
# But it doesn't stop there, as different industries can have different average P/E ratios.
        pe_ratio = round(float(stock_price)/eps,2)
        



# ----------------------- Average Price ----------------- #


        date = dt.datetime.now()
        endDate = dt.datetime(date.year, date.month, date.day)

# today 50 days ago
        fifty_days_ago = date - relativedelta(days=50)
        fifty_startDate = dt.datetime(fifty_days_ago.year, fifty_days_ago.month, fifty_days_ago.day)
        fifty_period = get_data.history(start=fifty_startDate,end=endDate)
        fifty_prices = []
        for x in fifty_period["Close"]:
            fifty_prices.append(round(x,2))
            
        fifty_average = average(fifty_prices)
        weekly_fifty_average = weekly_average(fifty_prices)

        fifty_moving_average = []
        for x in range(len(weekly_fifty_average)):
            if weekly_fifty_average[x-1] > weekly_fifty_average[x]:
                fifty_moving_average.append("+")
            else:
                fifty_moving_average.append("-")
        
        formatted_weekly_fifty_average = ""


# today 200 days ago
        two_h_days_ago = date - relativedelta(days=200)
        twoh_startDate = dt.datetime(two_h_days_ago.year, two_h_days_ago.month, two_h_days_ago.day)
        two_h_period = get_data.history(start=twoh_startDate,end=endDate)
        two_h_prices = []
        for x in two_h_period["Close"]:
            two_h_prices.append(round(x,2))


        two_h_average = average(two_h_prices)
        weekly_two_h_average = weekly_average(two_h_prices)

        two_h_moving_average = []
        for x in range(len(weekly_two_h_average)):
            if weekly_two_h_average[x-1] > weekly_two_h_average[x]:
                two_h_moving_average.append("+")
            else:
                two_h_moving_average.append("-")
        
        formatted_weekly_two_h_average = ""

    


# x days ago
        '''x_days_ago = date - relativedelta(days=insert num of days)
        x_startDate = dt.datetime(two_h_days_ago.year, x_days_ago.month, x_days_ago.day)
        x_period = get_data.history(start=x_startDate,end=endDate)
        x_prices = []
        for y in x_period["Close"]:
            x_prices.append(round(x,2))


        x_average = average(x_prices)
        weekly_x_average = weekly_average(x_prices)

        x_moving_average = []
        for x in range(len(weekly_x_average)):
            if weekly_x_average[x-1] > weekly_x_average[x]:
                x_moving_average.append("+")
            else:
                x_moving_average.append("-")'''




# --------------------------- NEWS API ------------------------- #



        my_parameters = {
            "apiKey":MY_KEY,
            "q":request.form['ticket'],
            "language":"en",
            "sortBy":"relevancy",
            "from":date-relativedelta(days=30)
        }

        response = requests.get(url=endpoint, params=my_parameters)
        data = response.json()
        articles = []
        for x in data['articles']:
            if isinstance(x['title'], type(None)):
                pass
            else:
                article = {
                    "source":x['source']['name'],
                    "title":x['title'],
                    "description":x['description'],
                    "link":x['url'],
                        }
                articles.append(article)
            if len(articles) >= N_ARTICLES:
                break
            
        return render_template('analyser.html',ticket=company_ticket, date=dt.datetime.now(),
                                #Income Statement
                                total_revenue = ['{:,.2f}'.format(int(x/1000)) for x in total_revenue],
                                gross_profit = ['{:,.2f}'.format(int(x/1000)) for x in gross_profit],
                                net_income = ['{:,.2f}'.format(int(x/1000)) for x in net_income],
                                #Balance Sheet
                                total_assets = ['{:,.2f}'.format(int(x/1000)) for x in total_assets],
                                total_liabilities = ['{:,.2f}'.format(int(x/1000)) for x in total_liabilities],
                                current_assets = ['{:,.2f}'.format(int(x/1000)) for x in current_assets],
                                current_liabilities = ['{:,.2f}'.format(int(x/1000)) for x in current_liabilities],
                                stockholders_equity = ['{:,.2f}'.format(int(x/1000)) for x in stockholders_equity],
                                shares_outstanding = '{:,.0f}'.format(int(shares_outstanding)),
                                stock_price = stock_price,
                                #Indices
                                gross_profit_margin = gross_profit_margin,
                                liquidity = liquidity,
                                roa = roa,
                                return_on_shar_eq = return_on_shar_eq,
                                debt_to_shareq = debt_to_shareq,
                                eps = eps, #single value
                                pe_ratio = pe_ratio, #single value
                                #Averages
                                fifty_average = fifty_average,
                                two_h_average = two_h_average,
                                fifty_chart = chart_maker(fifty_prices[::-1]),
                                two_h_chart = chart_maker(two_h_prices[::-1]),
                                #News
                                articles = articles
                                )
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)