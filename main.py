# main.py
import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_sp500_tickers():
    """
    Scrapes Wikipedia for the list of S&P 500 company tickers.
    """
    try:
        payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        sp500_tickers = payload[0]['Symbol'].values.tolist()
        print("Successfully fetched S&P 500 tickers.")
        return sp500_tickers
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        # Use a fallback list if Wikipedia fails
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM"]

def calculate_intrinsic_value(ticker_symbol):
    """
    Fetches financial data and calculates a simplified intrinsic value for a given company.
    
    DISCLAIMER: This is a highly simplified model for educational purposes and should not be used
    for actual investment decisions. The growth and discount rates are major assumptions.
    """
    try:
        stock = yf.Ticker(ticker_symbol)

        # --- 1. Get Free Cash Flow (FCF) ---
        cashflow = stock.cashflow
        if "Free Cash Flow" in cashflow.index:
            fcf = cashflow.loc['Free Cash Flow'].iloc[0]
        else: # Fallback calculation if FCF is not directly available
            op_cash = cashflow.loc['Total Cash From Operating Activities'].iloc[0]
            capex = cashflow.loc['Capital Expenditures'].iloc[0] # Capex is usually negative
            fcf = op_cash + capex
            
        if pd.isna(fcf) or fcf <= 0:
            print(f"[{ticker_symbol}] Could not determine a valid positive Free Cash Flow.")
            return None, None

        # --- 2. Set Assumptions ---
        perpetual_growth_rate = 0.025  # Assumed long-term GDP/inflation growth
        discount_rate = 0.07          # Weighted Average Cost of Capital (WACC) - represents risk
        short_term_growth_rate = 0.05 # Conservative 5-year growth estimate

        # --- 3. Project Future Cash Flows (5 years) and calculate Terminal Value ---
        future_fcf = [fcf * (1 + short_term_growth_rate)**i for i in range(1, 6)]
        terminal_value = (future_fcf[-1] * (1 + perpetual_growth_rate)) / (discount_rate - perpetual_growth_rate)

        # --- 4. Discount all future values back to today ---
        discounted_fcf = [cf / (1 + discount_rate)**(i+1) for i, cf in enumerate(future_fcf)]
        discounted_terminal_value = terminal_value / (1 + discount_rate)**5
        total_enterprise_value = sum(discounted_fcf) + discounted_terminal_value

        # --- 5. Calculate Equity Value and Intrinsic Value Per Share ---
        info = stock.info
        total_debt = info.get('totalDebt', 0)
        cash_and_equivalents = info.get('totalCash', 0)
        equity_value = total_enterprise_value - total_debt + cash_and_equivalents
        
        shares_outstanding = info.get('sharesOutstanding', 0)
        if shares_outstanding == 0:
            print(f"[{ticker_symbol}] Shares outstanding is zero, cannot calculate per-share value.")
            return None, None

        intrinsic_value_per_share = equity_value / shares_outstanding
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))

        return intrinsic_value_per_share, current_price

    except Exception as e:
        print(f"[{ticker_symbol}] An error occurred: {e}")
        return None, None

MAG7 = {"AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"}

def analyze_companies(tickers):
    results = []
    for ticker in tickers:
        print(f"\nAnalyzing {ticker}...")
        intrinsic_value, current_price = calculate_intrinsic_value(ticker)
        if intrinsic_value is not None and current_price is not None:
            margin_of_safety = (1 - (current_price / intrinsic_value)) * 100 if intrinsic_value > 0 else -100
            verdict = "Undervalued" if intrinsic_value > current_price else "Overvalued"
            results.append({
                "Ticker": ticker,
                "Intrinsic Value": f"${intrinsic_value:,.2f}",
                "Current Price": f"${current_price:,.2f}",
                "Margin of Safety": f"{margin_of_safety:.2f}%",
                "Verdict": verdict
            })
    return results

if __name__ == "__main__":
    top_companies = get_sp500_tickers()
    all_results = analyze_companies(top_companies)
    mag7_results = [r for r in all_results if r["Ticker"] in MAG7]

    # Create and display only the Magnificent 7 table
    mag7_df = pd.DataFrame(mag7_results)
    print("\n--- Magnificent 7 Intrinsic Value Analysis (Simplified DCF Model) ---")
    print(mag7_df.to_string(index=False))
    print("\nDisclaimer: This is for educational purposes only and not financial advice.")