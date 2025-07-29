# main_smarter.py
import yfinance as yf
import pandas as pd

# --- Tiered Assumptions: THIS IS WHERE THE JUDGMENT HAPPENS ---
# We define different assumptions for different types of businesses.
# This is a massive improvement over a one-size-fits-all model.
COMPANY_TIERS = {
    "Tier 1: Stalwarts": {
        "tickers": {"MSFT", "GOOGL", "GOOG", "V", "MA", "AAPL", "ADBE"},
        "assumptions": {"short_term_growth": 0.08, "discount_rate": 0.085, "perpetual_growth": 0.025}
    },
    "Tier 2: High-Growth": {
        "tickers": {"MELI", "SNOW", "NVDA", "TSLA", "AMD", "SHOP"},
        "assumptions": {"short_term_growth": 0.15, "discount_rate": 0.12, "perpetual_growth": 0.03}
    },
    "Tier 3: Mature Value": {
        "tickers": {"BRK-B", "COST", "WMT", "TMO"},
        "assumptions": {"short_term_growth": 0.04, "discount_rate": 0.08, "perpetual_growth": 0.02}
    },
    "Tier 4: Turnarounds/Special": {
        "tickers": {"PYPL", "SQ", "META", "NFLX", "UBER"},
        "assumptions": {"short_term_growth": 0.05, "discount_rate": 0.11, "perpetual_growth": 0.02}
    }
}

def get_dcf_assumptions(ticker):
    """Finds the correct assumptions for a ticker based on its tier."""
    for tier_info in COMPANY_TIERS.values():
        if ticker in tier_info["tickers"]:
            return tier_info["assumptions"]
    # Default assumptions if ticker is not in any tier
    print(f"[{ticker}] Using default assumptions.")
    return {"short_term_growth": 0.05, "discount_rate": 0.10, "perpetual_growth": 0.025}

# --- Curated Focus List ---
# A more focused list of companies with strong business models worth analyzing.
FOCUS_LIST = [
    # Magnificent 7
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META",
    # Slatwards / High-Quality Focus
    "BRK-B", "V", "MA", "COST", "ADBE", "CRM", "PYPL", "MELI", "SQ", "SNOW", "UBER", "NFLX"
]
# Add GOOG for comparison if not already present
if "GOOG" not in FOCUS_LIST: FOCUS_LIST.append("GOOG")


def compute_intrinsic_value(ticker, assumptions):
    """
    Calculates intrinsic value using specific assumptions for that company.
    """
    try:
        stock = yf.Ticker(ticker)
        cashflow = stock.cashflow
        if "Free Cash Flow" not in cashflow.index or cashflow.loc['Free Cash Flow'].iloc[0] <= 0:
            print(f"[{ticker}] Using Operating Cash Flow - CapEx as FCF is invalid.")
            op_cash = cashflow.loc['Total Cash From Operating Activities'].iloc[0]
            capex = stock.loc['Capital Expenditures'].iloc[0]
            fcf = op_cash + capex
        else:
            fcf = cashflow.loc['Free Cash Flow'].iloc[0]

        if pd.isna(fcf) or fcf <= 0:
            print(f"[{ticker}] Cannot use non-positive Free Cash Flow for DCF.")
            return None, None

        # Unpack assumptions
        short_term_growth = assumptions['short_term_growth']
        discount_rate = assumptions['discount_rate']
        perpetual_growth = assumptions['perpetual_growth']

        projected_fcf = [fcf * (1 + short_term_growth)**i for i in range(1, 6)]
        terminal_value = (projected_fcf[-1] * (1 + perpetual_growth)) / (discount_rate - perpetual_growth)

        discounted_fcf = [cf / (1 + discount_rate)**(i+1) for i, cf in enumerate(projected_fcf)]
        discounted_terminal = terminal_value / (1 + discount_rate)**5
        enterprise_value = sum(discounted_fcf) + discounted_terminal

        info = stock.info
        total_debt = info.get('totalDebt', 0)
        cash_equiv = info.get('totalCash', 0)
        equity_value = enterprise_value - total_debt + cash_equiv
        shares = info.get('sharesOutstanding', 0)

        if shares == 0: return None, None
        
        intrinsic_per_share = equity_value / shares
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        return intrinsic_per_share, current_price

    except Exception as e:
        print(f"[{ticker}] An error occurred: {e}")
        return None, None

def fetch_pe_ratio(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('trailingPE')
    except Exception:
        return None

# --- Main Execution ---
if __name__ == "__main__":
    analysis_results = []
    # Using the curated FOCUS_LIST
    for ticker in sorted(list(set(FOCUS_LIST))):
        print(f"\nAnalyzing {ticker}...")
        assumptions = get_dcf_assumptions(ticker)
        intrinsic, price = compute_intrinsic_value(ticker, assumptions)
        
        pe_ratio = fetch_pe_ratio(ticker)
        pe_verdict = "High P/E" if pe_ratio and pe_ratio > 25 else ("Low P/E" if pe_ratio else "N/A")

        if intrinsic is not None and price is not None:
            margin = (1 - (price / intrinsic)) * 100 if intrinsic > 0 else -100
            verdict = "Undervalued" if intrinsic > price else "Overvalued"
            analysis_results.append({
                "Ticker": ticker,
                "Intrinsic Value": f"${intrinsic:,.2f}",
                "Current Price": f"${price:,.2f}",
                "Margin of Safety": f"{margin:.2f}%",
                "Verdict": verdict,
                "P/E Ratio": f"{pe_ratio:.2f}" if pe_ratio else "N/A",
                "P/E Verdict": pe_verdict
            })

    # Display Results
    print("\n--- Focused Analysis with Tiered Assumptions ---")
    df = pd.DataFrame(analysis_results)
    print(df.to_string(index=False))
    print("\nDisclaimer: This is for educational purposes only. Intrinsic values are highly sensitive to assumptions.")
