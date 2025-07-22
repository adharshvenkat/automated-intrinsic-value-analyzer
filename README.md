# Automated Intrinsic Value Analyzer

This script provides an automated analysis of two key groups of public companies:

- **Magnificent 7**: The seven largest and most influential US tech companies.
- **Stalwarts**: A curated list of high-potential, innovative, or disruptive companies across various sectors and themes (excluding any overlap with the Magnificent 7).

For each company in both groups, the script computes:

- **Intrinsic Value per Share** using a simplified Discounted Cash Flow (DCF) model
- **Current Market Price**
- **Margin of Safety** (relative difference between intrinsic value and market price)
- **Valuation Verdict** (Undervalued/Overvalued)
- **Trailing P/E Ratio** (if available)
- **P/E Verdict** (High/Low P/E based on a threshold)

The results are displayed as two clear tables in the terminal:
- One for the Magnificent 7
- One for the Stalwarts

Each table combines both DCF and P/E analysis for easy comparison.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python main.py
   ```

## Notes
- No API keys or credentials are required.
- The script does not analyze the entire S&P 500, only the two focused lists.
- All data is fetched live using Yahoo Finance via the `yfinance` package.
- The script is for educational purposes only and not financial advice.

## Customization
- You can easily modify the `MAGNIFICENT_7` and `SLATWARDS` lists in `main.py` to analyze other companies or themes.

---

**Disclaimer:** This tool is for educational purposes only and not financial advice. Always do your own research before making investment decisions.
