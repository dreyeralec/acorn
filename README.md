Acorn is a fully autonomous securities trading system using the IB Gateway from Interactive Brokers and ChatGPT as its brain.
Acorn uses Telegram to interface with the user, allowing the user to control the system from anywhere.

# Configuration
```
  account_type: ("paper", "live") decides what account type to use
  data_relevancy: 1 for live data (requires subscription), 2 for frozen (market closed, free), 3 for 15-20 minute delay (free)
  limit_MoE: (0 - 1) margin of error for AI generated limit prices vs actual market price
  model: OpenAI model to be used
  timeout: time the user has to respond to a trade proposition on telegram
```