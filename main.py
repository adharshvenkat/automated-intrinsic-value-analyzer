# main.py
import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# --- Intrinsic Value Calculation ---
def compute_intrinsic_value(ticker):
    """
    Calculates a simplified intrinsic value for a given ticker using a DCF model.
    Returns (intrinsic_value_per_share, current_price) or (None, None) on error.
    """
    try:
        stock = yf.Ticker(ticker)
        cashflow = stock.cashflow
        if "Free Cash Flow" in cashflow.index:
            fcf = cashflow.loc['Free Cash Flow'].iloc[0]
        else:
            op_cash = cashflow.loc['Total Cash From Operating Activities'].iloc[0]
            capex = cashflow.loc['Capital Expenditures'].iloc[0]
            fcf = op_cash + capex
        if pd.isna(fcf) or fcf <= 0:
            print(f"[{ticker}] Could not determine a valid positive Free Cash Flow.")
            return None, None
        # DCF assumptions
        perpetual_growth = 0.025
        discount_rate = 0.07
        short_term_growth = 0.05
        # Project FCF and terminal value
        projected_fcf = [fcf * (1 + short_term_growth)**i for i in range(1, 6)]
        terminal_value = (projected_fcf[-1] * (1 + perpetual_growth)) / (discount_rate - perpetual_growth)
        # Discount to present value
        discounted_fcf = [cf / (1 + discount_rate)**(i+1) for i, cf in enumerate(projected_fcf)]
        discounted_terminal = terminal_value / (1 + discount_rate)**5
        enterprise_value = sum(discounted_fcf) + discounted_terminal
        # Equity value and per-share value
        info = stock.info
        total_debt = info.get('totalDebt', 0)
        cash_equiv = info.get('totalCash', 0)
        equity_value = enterprise_value - total_debt + cash_equiv
        shares = info.get('sharesOutstanding', 0)
        if shares == 0:
            print(f"[{ticker}] Shares outstanding is zero, cannot calculate per-share value.")
            return None, None
        intrinsic_per_share = equity_value / shares
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        return intrinsic_per_share, current_price
    except Exception as e:
        print(f"[{ticker}] An error occurred: {e}")
        return None, None

# --- Company Groups ---
MAGNIFICENT_7 = {"AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"}

# Slatwards: High-potential, innovative, or disruptive companies (not in Mag 7)
SLATWARDS = [
    "BRK-B",  # Berkshire Hathaway
    "UBER",   # Uber Technologies
    "NFLX",   # Netflix
    "COST",   # Costco Wholesale
    "WMT",    # Walmart
    "GOOG",   # Alphabet (Class C)
    "AMD",    # Advanced Micro Devices
    "AVGO",   # Broadcom
    "ADBE",   # Adobe
    "CRM",    # Salesforce
    "V",      # Visa
    "MA",     # Mastercard
    "LLY",    # Eli Lilly
    "ORCL",   # Oracle
    # Additional high-potential or thematic leaders:
    "SHOP",   # Shopify (e-commerce platform)
    "SNOW",   # Snowflake (cloud data)
    "PLTR",   # Palantir (data analytics)
    "SQ",     # Block/Square (fintech)
    "ASML",   # ASML (semiconductor equipment)
    "SPOT",   # Spotify (streaming)
    "PYPL",   # PayPal (fintech)
    "MELI",   # MercadoLibre (LatAm e-commerce/fintech)
    "TMO",    # Thermo Fisher (life sciences)
    "REGN",   # Regeneron (biotech)
    "NOW",    # ServiceNow (cloud workflow)
    "ZS",     # Zscaler (cybersecurity)
    "TEAM",   # Atlassian (collaboration software)
    "ROKU"    # Roku (streaming platform)
]

# Remove any companies from SLATWARDS that are in MAGNIFICENT_7
SLATWARDS = [ticker for ticker in SLATWARDS if ticker not in MAGNIFICENT_7]

# --- Analysis Function ---
def analyze_company_group(ticker_list):
    """
    Analyzes a list of tickers and returns a summary list of dictionaries.
    """
    summary = []
    for ticker in ticker_list:
        print(f"\nAnalyzing {ticker}...")
        intrinsic, price = compute_intrinsic_value(ticker)
        if intrinsic is not None and price is not None:
            margin = (1 - (price / intrinsic)) * 100 if intrinsic > 0 else -100
            verdict = "Undervalued" if intrinsic > price else "Overvalued"
            summary.append({
                "Ticker": ticker,
                "Intrinsic Value": f"${intrinsic:,.2f}",
                "Current Price": f"${price:,.2f}",
                "Margin of Safety": f"{margin:.2f}%",
                "Verdict": verdict
            })
    return summary

# --- Multiples Valuation Function ---
def fetch_pe_ratio(ticker):
    """
    Fetches the trailing P/E ratio for a given ticker using yfinance.
    Returns the P/E ratio or None if unavailable.
    """
    try:
        stock = yf.Ticker(ticker)
        pe_ratio = stock.info.get('trailingPE', None)
        return pe_ratio
    except Exception as e:
        print(f"[{ticker}] Error fetching P/E ratio: {e}")
        return None

def analyze_with_multiples(ticker_list):
    """
    Analyzes a list of tickers and returns a summary list of dictionaries using P/E ratio.
    """
    summary = []
    for ticker in ticker_list:
        print(f"\nFetching P/E for {ticker}...")
        pe = fetch_pe_ratio(ticker)
        verdict = "High P/E" if pe and pe > 25 else ("Low P/E" if pe else "N/A")
        summary.append({
            "Ticker": ticker,
            "P/E Ratio": f"{pe:.2f}" if pe else "N/A",
            "P/E Verdict": verdict
        })
    return summary

# --- Main Execution ---
if __name__ == "__main__":
    # Only analyze the two lists
    mag7 = list(MAGNIFICENT_7)
    slatwards = SLATWARDS

    # DCF and P/E for Magnificent 7
    mag7_dcf = analyze_company_group(mag7)
    mag7_pe = analyze_with_multiples(mag7)
    mag7_combined = []
    for dcf, pe in zip(mag7_dcf, mag7_pe):
        combined = dcf.copy()
        combined["P/E Ratio"] = pe["P/E Ratio"]
        combined["P/E Verdict"] = pe["P/E Verdict"]
        mag7_combined.append(combined)

    # DCF and P/E for Slatwards
    slatward_dcf = analyze_company_group(slatwards)
    slatward_pe = analyze_with_multiples(slatwards)
    slatward_combined = []
    for dcf, pe in zip(slatward_dcf, slatward_pe):
        combined = dcf.copy()
        combined["P/E Ratio"] = pe["P/E Ratio"]
        combined["P/E Verdict"] = pe["P/E Verdict"]
        slatward_combined.append(combined)

    # Display Magnificent 7
    print("\n--- Magnificent 7: DCF & P/E Analysis ---")
    print(pd.DataFrame(mag7_combined).to_string(index=False))

    # Display Slatwards
    print("\n--- Slatwards (High Potential Companies): DCF & P/E Analysis ---")
    print(pd.DataFrame(slatward_combined).to_string(index=False))

    print("\nDisclaimer: This is for educational purposes only and not financial advice.")