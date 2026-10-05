import yaml
import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    def __init__(self, config_file):
        self.load_config(config_file)


    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        self.ibg_port = _get_port(config["ib"]["account_type"])
        self.model = config["llm"]["model"]
        self.timeout = config["telegram"]["timeout"]
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.telegram_bot_key = os.getenv("TELEGRAM_BOT_KEY")


def _get_port(config: str) -> int:
    if config == "paper":
        return 4002
    if config == "live":
        return 4001
    else:
        raise NotImplementedError(f"No port assigned for: {config}")


config = Config("config.yaml")