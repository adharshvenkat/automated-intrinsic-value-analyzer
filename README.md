# Automated Intrinsic Value Analyzer

This project contains a Python script that analyzes stock intrinsic value and runs daily using GitHub Actions.

## Overview

The script performs the following actions:
1.  Fetches the current list of S&P 500 company tickers from Wikipedia.
2.  For a sample of companies, it retrieves key financial data using the `yfinance` library.
3.  It calculates an estimated intrinsic value based on a simplified **Discounted Cash Flow (DCF)** model.
4.  It prints a summary table comparing the calculated intrinsic value against the current stock price.

## Automation
This script is configured to run automatically every day at 8:00 AM UTC via a GitHub Actions workflow. The results of each daily run can be viewed in the "Actions" tab of this repository.

### Disclaimer
**This is an educational tool and should not be used for making actual investment decisions.** The financial model is highly simplified, and the assumptions for growth and discount rates are fixed estimates. Real-world financial analysis requires deep, nuanced research.