# Forex Trading Bot

An automated trading bot for MetaTrader 5 that implements a moving average crossover strategy with RSI and MACD filters.

## Features

- Automated trading on MetaTrader 5
- Moving Average Crossover strategy
- RSI and MACD filters for better entry/exit points
- Real-time market data analysis
- Position management with stop-loss and take-profit
- Logging system for monitoring and debugging
- Optional Telegram notifications

## Prerequisites

- Python 3.8 or higher
- MetaTrader 5 terminal installed and configured
- A broker account with MT5 access
- (Optional) Telegram bot token and chat ID for notifications

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Copy the environment example file and configure your settings:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your MT5 credentials and trading parameters.

## Usage

1. Make sure MetaTrader 5 is running and you're logged in.

2. Run the trading bot:
```bash
python trading_bot.py
```

## Strategy Details

The bot implements a combination of technical indicators:

- Moving Average Crossover (20 and 50 periods)
- RSI (14 periods) for overbought/oversold conditions
- MACD for trend confirmation

### Entry Rules
- Buy when short MA crosses above long MA
- Sell when short MA crosses below long MA
- RSI must not be in extreme zones (>70 or <30)
- MACD must confirm the trend direction

### Exit Rules
- Close long positions when RSI > 70 or MACD crosses below signal line
- Close short positions when RSI < 30 or MACD crosses above signal line

## Risk Warning

Trading forex involves significant risk of loss. This bot is provided for educational purposes only. Always test thoroughly in a demo account before using with real money.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Forex Trading Lot Size Guide

## Understanding Lot Sizes and Risk Management

### Standard Lot Sizes in Forex:
- 1.00 lot = 100,000 units
- 0.10 lot = 10,000 units
- 0.05 lot = 5,000 units
- 0.01 lot = 1,000 units (minimum standard lot)

### Lot Size Calculator Table
(Assuming XAUUSDm/Gold price at $2,000 per unit)

| Account Balance | Risk % | Risk Amount | Calculated Lot | Actual Lot (min 0.01) | Required Balance for Safe Trading |
|----------------|---------|-------------|----------------|----------------------|-----------------------------------|
| $10            | 0.1%    | $0.01      | 0.000005      | 0.01                 | $10 (minimum)                     |
| $100           | 0.1%    | $0.10      | 0.00005       | 0.01                 | $100 (minimum)                    |
| $1,000         | 0.1%    | $1.00      | 0.0005        | 0.01                 | $1,000 (minimum)                  |
| $5,000         | 0.1%    | $5.00      | 0.0025        | 0.01                 | $5,000 (minimum)                  |
| $10,000        | 0.1%    | $10.00     | 0.005         | 0.01                 | $10,000 (minimum)                 |
| $50,000        | 0.1%    | $50.00     | 0.025         | 0.05                 | $50,000 (minimum)                 |
| $100,000       | 0.1%    | $100.00    | 0.05          | 0.10                 | $100,000 (minimum)                |

### How to Calculate Your Lot Size

1. Basic Formula:
   ```
   Risk Amount = Account Balance × Risk Percentage
   Calculated Lot = Risk Amount ÷ Current Price
   ```

2. Example Calculations:
   - For $100 account with 0.1% risk:
     - Risk Amount = $100 × 0.001 = $0.10
     - If Gold price is $2,000:
     - Calculated Lot = $0.10 ÷ $2,000 = 0.00005
     - Actual Lot = 0.01 (minimum lot size)

### Important Notes:

1. Minimum Lot Size:
   - Most brokers have a minimum lot size of 0.01
   - The bot will automatically use 0.01 if calculated lot is smaller

2. Safe Trading Guidelines:
   - Never risk more than 1% of your account per trade
   - Recommended risk: 0.1% to 0.5% per trade
   - Always use stop loss orders

3. Account Size Recommendations:
   - For 0.01 lots: Minimum $100
   - For 0.05 lots: Minimum $5,000
   - For 0.10 lots: Minimum $10,000
   - For 1.00 lots: Minimum $100,000

### Risk Management Tips:

1. Always use proper risk management
2. Never trade more than you can afford to lose
3. Start with smaller lot sizes while learning
4. Increase lot sizes only as your account grows
5. Keep risk per trade below 1% of your account

### Warning:
- Trading with lot sizes larger than your account can safely handle is extremely risky
- One losing trade could wipe out your entire account
- Always trade within your means and use proper risk management

### Risk Percentage Calculator Table
(Assuming XAUUSDm/Gold price at $2,000 per unit)

| Risk Percentage | Risk Amount Formula | $100 Account | $1,000 Account | $10,000 Account | Recommended For |
|-----------------|---------------------|--------------|----------------|-----------------|-----------------|
| 0.001 (0.1%)    | balance * 0.001     | $0.10        | $1.00         | $10.00         | Very Safe       |
| 0.002 (0.2%)    | balance * 0.002     | $0.20        | $2.00         | $20.00         | Safe            |
| 0.005 (0.5%)    | balance * 0.005     | $0.50        | $5.00         | $50.00         | Moderate        |
| 0.01 (1%)       | balance * 0.01      | $1.00        | $10.00        | $100.00        | Aggressive      |
| 0.02 (2%)       | balance * 0.02      | $2.00        | $20.00        | $200.00        | Very Risky      |
| 0.05 (5%)       | balance * 0.05      | $5.00        | $50.00        | $500.00        | Extremely Risky |

### How to Change Risk Percentage

1. Current Setting (Very Safe):
   ```python
   risk_amount = balance * 0.001  # 0.1% risk
   ```

2. For More Aggressive Trading:
   ```python
   risk_amount = balance * 0.005  # 0.5% risk
   ```

3. For Very Aggressive Trading:
   ```python
   risk_amount = balance * 0.01   # 1% risk
   ```

### Risk Level Guidelines:

1. Very Safe (0.1%):
   - Best for beginners
   - Maximum 10 losing trades before 1% account loss
   - Recommended for learning

2. Safe (0.2%):
   - Good for experienced traders
   - Maximum 5 losing trades before 1% account loss
   - Balanced risk/reward

3. Moderate (0.5%):
   - For confident traders
   - Maximum 2 losing trades before 1% account loss
   - Higher potential returns

4. Aggressive (1%):
   - For professional traders
   - One losing trade = 1% account loss
   - Requires strict risk management

5. Very Risky (2%+):
   - Not recommended
   - High chance of account blowup
   - Avoid unless you're very experienced

### Warning:
- Higher risk percentages mean higher potential losses
- Always start with lower risk (0.1% - 0.5%)
- Never risk more than you can afford to lose
- Test your strategy with lower risk first

### Risk to Lot Size Calculator
(Assuming XAUUSDm/Gold price at $2,000 per unit)

| Account Balance | Risk % | Risk Amount | Calculated Lot | Actual Lot (min 0.01) | Notes |
|----------------|---------|-------------|----------------|----------------------|-------|
| $100           | 0.1%    | $0.10      | 0.00005       | 0.01                 | Minimum lot |
| $100           | 0.5%    | $0.50      | 0.00025       | 0.01                 | Minimum lot |
| $100           | 1%      | $1.00      | 0.0005        | 0.01                 | Minimum lot |
| $1,000         | 0.1%    | $1.00      | 0.0005        | 0.01                 | Minimum lot |
| $1,000         | 0.5%    | $5.00      | 0.0025        | 0.01                 | Minimum lot |
| $1,000         | 1%      | $10.00     | 0.005         | 0.01                 | Minimum lot |
| $5,000         | 0.1%    | $5.00      | 0.0025        | 0.01                 | Minimum lot |
| $5,000         | 0.5%    | $25.00     | 0.0125        | 0.05                 | Safe for 0.05 lots |
| $5,000         | 1%      | $50.00     | 0.025         | 0.05                 | Safe for 0.05 lots |
| $10,000        | 0.1%    | $10.00     | 0.005         | 0.01                 | Minimum lot |
| $10,000        | 0.5%    | $50.00     | 0.025         | 0.05                 | Safe for 0.05 lots |
| $10,000        | 1%      | $100.00    | 0.05          | 0.10                 | Safe for 0.10 lots |

### Lot Size Requirements:

1. For 0.01 lots (minimum):
   - Any account size with any risk % will use 0.01
   - This is the minimum lot size allowed

2. For 0.05 lots:
   - Need at least $5,000 account
   - Use 0.5% or 1% risk
   - Example: $5,000 * 0.005 = $25 risk

3. For 0.10 lots:
   - Need at least $10,000 account
   - Use 1% risk
   - Example: $10,000 * 0.01 = $100 risk

### How to Calculate Your Lot Size:

1. Basic Formula:
   ```
   Risk Amount = Account Balance × Risk Percentage
   Calculated Lot = Risk Amount ÷ Current Price
   ```

2. Example for 0.05 lots:
   - Account: $5,000
   - Risk: 0.5% (0.005)
   - Risk Amount: $5,000 × 0.005 = $25
   - If Gold price is $2,000:
   - Calculated Lot: $25 ÷ $2,000 = 0.0125
   - Actual Lot: 0.05 (minimum for this risk level)

### Important Notes:
- Minimum lot size is 0.01
- To trade 0.05 lots safely, need $5,000+ account
- To trade 0.10 lots safely, need $10,000+ account
- Higher risk % = larger lot sizes possible
- But higher risk % = higher chance of losses

### Risk Management Tips:

1. Always use proper risk management
2. Never trade more than you can afford to lose
3. Start with smaller lot sizes while learning
4. Increase lot sizes only as your account grows
5. Keep risk per trade below 1% of your account

### Warning:
- Trading with lot sizes larger than your account can safely handle is extremely risky
- One losing trade could wipe out your entire account
- Always trade within your means and use proper risk management

### Risk Percentage Calculator Table
(Assuming XAUUSDm/Gold price at $2,000 per unit)

| Risk Percentage | Risk Amount Formula | $100 Account | $1,000 Account | $10,000 Account | Recommended For |
|-----------------|---------------------|--------------|----------------|-----------------|-----------------|
| 0.001 (0.1%)    | balance * 0.001     | $0.10        | $1.00         | $10.00         | Very Safe       |
| 0.002 (0.2%)    | balance * 0.002     | $0.20        | $2.00         | $20.00         | Safe            |
| 0.005 (0.5%)    | balance * 0.005     | $0.50        | $5.00         | $50.00         | Moderate        |
| 0.01 (1%)       | balance * 0.01      | $1.00        | $10.00        | $100.00        | Aggressive      |
| 0.02 (2%)       | balance * 0.02      | $2.00        | $20.00        | $200.00        | Very Risky      |
| 0.05 (5%)       | balance * 0.05      | $5.00        | $50.00        | $500.00        | Extremely Risky |

### How to Change Risk Percentage

1. Current Setting (Very Safe):
   ```python
   risk_amount = balance * 0.001  # 0.1% risk
   ```

2. For More Aggressive Trading:
   ```python
   risk_amount = balance * 0.005  # 0.5% risk
   ```

3. For Very Aggressive Trading:
   ```python
   risk_amount = balance * 0.01   # 1% risk
   ```

### Risk Level Guidelines:

1. Very Safe (0.1%):
   - Best for beginners
   - Maximum 10 losing trades before 1% account loss
   - Recommended for learning

2. Safe (0.2%):
   - Good for experienced traders
   - Maximum 5 losing trades before 1% account loss
   - Balanced risk/reward

3. Moderate (0.5%):
   - For confident traders
   - Maximum 2 losing trades before 1% account loss
   - Higher potential returns

4. Aggressive (1%):
   - For professional traders
   - One losing trade = 1% account loss
   - Requires strict risk management

5. Very Risky (2%+):
   - Not recommended
   - High chance of account blowup
   - Avoid unless you're very experienced

### Warning:
- Higher risk percentages mean higher potential losses
- Always start with lower risk (0.1% - 0.5%)
- Never risk more than you can afford to lose
- Test your strategy with lower risk first 