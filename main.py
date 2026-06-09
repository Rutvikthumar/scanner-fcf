import yfinance as yf
import pandas as pd
import time

def get_allocator_metrics(ticker_list):
    results = []
    
    print(f"Analyzing {len(ticker_list)} tickers...")
    
    for symbol in ticker_list:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # 1. Fetch Key Data
            # Note: We use .get() to prevent crashes if data is missing
            market_cap = info.get('marketCap')
            total_debt = info.get('totalDebt', 0)
            total_equity = info.get('totalStockholderEquity', 1)
            revenue_growth = info.get('revenueGrowth', 0)
            roic = info.get('returnOnInvestedCapital', 0)
            
            # 2. Get Cash Flow Data
            cash_flow = stock.cashflow
            if cash_flow.empty:
                continue
                
            op_cash_flow = cash_flow.loc['Operating Cash Flow'][0]
            cap_ex = abs(cash_flow.loc['Capital Expenditure'][0])
            fcf = op_cash_flow - cap_ex
            
            # 3. Calculations
            fcf_yield = (fcf / market_cap) * 100
            debt_to_equity = total_debt / total_equity
            
            # 4. Strict "Allocator" Filters
            # ROIC > 15%, FCF Yield > 5%, Debt/Equity < 0.5, Revenue Growth > 10%
            if (roic and roic >= 0.15) and (fcf_yield >= 5) and \
               (debt_to_equity < 0.5) and (revenue_growth >= 0.10):
                
                results.append({
                    'Ticker': symbol,
                    'FCF_Yield': round(fcf_yield, 2),
                    'ROIC': round(roic * 100, 2),
                    'Rev_Growth': round(revenue_growth * 100, 2),
                    'Debt_to_Equity': round(debt_to_equity, 2)
                })
            
            # Pause to avoid hitting API rate limits
            time.sleep(1) 
            
        except Exception as e:
            print(f"Skipping {symbol}: {e}")
            
    return pd.DataFrame(results)

# YOUR LIST HERE
# Example: Add mid-caps that you think are "Quality"
my_watchlist = ['GFL', 'RSG', 'WM', 'JCI', 'FAST', 'ROP'] 
df = get_allocator_metrics(my_watchlist)

# Save to Excel
df.to_csv('allocator_quality_scan.csv', index=False)
print("--- Quality Scan Complete ---")
print(df)
