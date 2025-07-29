import yfinance as yf
import pandas as pd
import numpy as np

COMPANY_TIERS = {
    "Tier 1: Stalwarts": {
        "tickers": {"MSFT", "GOOGL", "GOOG", "V", "MA", "AAPL", "ADBE"},
        "assumptions": {"short_term_growth": 0.08, "discount_rate": 0.09, "perpetual_growth": 0.025}
    },
    "Tier 2: High-Growth": {
        "tickers": {"NVDA", "MELI"},
        "assumptions": {"short_term_growth": 0.18, "discount_rate": 0.13, "perpetual_growth": 0.03}
    },
    "Tier 3: Mature Value": {
        "tickers": {"BRK-B", "COST", "WMT", "CRM", "JNJ", "PG"},
        "assumptions": {"short_term_growth": 0.05, "discount_rate": 0.08, "perpetual_growth": 0.02}
    },
    "Tier 4: Special/Turnaround": {
        "tickers": {"PYPL", "SQ", "META", "NFLX", "UBER", "AMZN"},
        "assumptions": {"short_term_growth": 0.07, "discount_rate": 0.12, "perpetual_growth": 0.02}
    }
}

WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "V", "MA",
    "JNJ", "PG", "COST", "WMT", "ADBE", "CRM", "NFLX", "PYPL", "SQ", "UBER", "MELI"
]

def get_company_tier(ticker):
    for tier_name, tier_info in COMPANY_TIERS.items():
        if ticker in tier_info["tickers"]:
            return tier_name, tier_info["assumptions"]
    return "Uncategorized", {"short_term_growth": 0.05, "discount_rate": 0.10, "perpetual_growth": 0.02}

def analyze_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        tier_name, assumptions = get_company_tier(ticker)
        
        cashflow = stock.cashflow
        if 'Free Cash Flow' in cashflow.index:
            fcf_history = cashflow.loc['Free Cash Flow']
        else:
            op_cash = cashflow.loc['Total Cash From Operating Activities']
            cap_ex = cashflow.loc['Capital Expenditures']
            fcf_history = op_cash + cap_ex
            
        fcf_last_3_years = fcf_history.dropna().head(3)
        if fcf_last_3_years.empty:
            return {"Ticker": ticker, "Verdict": "No FCF Data"}
            
        normalized_fcf = np.mean(fcf_last_3_years)

        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return {"Ticker": ticker, "Verdict": "No Price Data"}

        result = {
            "Ticker": ticker,
            "Tier": tier_name.split(':')[1].strip(),
            "Current Price": f"${current_price:,.2f}",
            "P/E Ratio": info.get('trailingPE')
        }

        if normalized_fcf <= 0:
            result.update({"Verdict": "Negative FCF", "Intrinsic Value": "N/A", "Margin of Safety": "N/A"})
            return result

        short_term_growth = assumptions['short_term_growth']
        discount_rate = assumptions['discount_rate']
        perpetual_growth = assumptions['perpetual_growth']
        YEARS_TO_PROJECT = 5

        projected_fcf = [normalized_fcf * (1 + short_term_growth)**i for i in range(1, YEARS_TO_PROJECT + 1)]
        terminal_value = (projected_fcf[-1] * (1 + perpetual_growth)) / (discount_rate - perpetual_growth)
        
        if terminal_value < 0:
             result.update({"Verdict": "Negative Terminal Value", "Intrinsic Value": "N/A", "Margin of Safety": "N/A"})
             return result

        discounted_fcf = [cf / (1 + discount_rate)**(i+1) for i, cf in enumerate(projected_fcf)]
        discounted_terminal = terminal_value / (1 + discount_rate)**YEARS_TO_PROJECT
        enterprise_value = sum(discounted_fcf) + discounted_terminal

        total_debt = info.get('totalDebt', 0)
        cash_equiv = info.get('totalCash', 0)
        shares = info.get('sharesOutstanding', 0)

        if not shares:
            result.update({"Verdict": "No Share Data", "Intrinsic Value": "N/A", "Margin of Safety": "N/A"})
            return result
            
        equity_value = enterprise_value - total_debt + cash_equiv
        intrinsic_per_share = equity_value / shares
        margin = (1 - (current_price / intrinsic_per_share)) * 100 if intrinsic_per_share > 0 else -100
        verdict = "Undervalued" if current_price < intrinsic_per_share else "Overvalued"

        result.update({
            "Intrinsic Value": f"${intrinsic_per_share:,.2f}",
            "Margin of Safety": f"{margin:.2f}%",
            "Verdict": verdict
        })
        return result

    except Exception as e:
        return {"Ticker": ticker, "Verdict": f"Error: {e}"}

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    analysis_results = [analyze_ticker(ticker) for ticker in sorted(list(set(WATCHLIST)))]
    final_df = pd.DataFrame(analysis_results)
    
    print("\n--- Final Investment Filter ---")
    print(final_df.to_string(index=False))
    print("\nDisclaimer: This is a quantitative filter, not financial advice. Judgment is required.")
