Acorn is a fully autonomous securities trading system using the IB Gateway from Interactive Brokers and ChatGPT as its brain.
Acorn uses Telegram to interface with the user, allowing the user to control the system from anywhere.

## Configuration - (config.yaml)
```
  account_type: ("paper", "live") decides what account type to use
  data_relevancy: 1 for live data (requires subscription), 2 for frozen (market closed, free), 3 for 15-20 minute delay (free)
  limit_MoE: (0 - 1) margin of error for AI generated limit prices vs actual market price
  model: OpenAI model to be used
  timeout: time the user has to respond to a trade proposition on telegram
  wake_ups:
    - hour: hour of the wakeup
      minute: minute of the wakeup
      second: second of the wakeup
      type: "trade", "analysis"; event ran during wake up
```

## Event types
Events ran during wake up

**Trade** (prompts/TRADE.txt)

Model looks at portfolio and account data and sends user any actions it wants to take via telegram.

**Analysis** (prompts/ANALYSIS.txt)

Model reviews portfolio performance, gives user an overview of how the portfolio is doing vs. broader market.

## In the future
- Support for other AI models
- Pipelines for providing real data to the model instead of relying on its web-search tool
- Configurable wake-up times
- Containerized to run in the cloud
