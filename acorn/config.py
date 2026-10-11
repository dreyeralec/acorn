import yaml
import os
from dotenv import load_dotenv

_ = load_dotenv()


class Config:
    def __init__(self, config_file) -> None:
        self.load_config(config_file)


    def load_config(self, config_file) -> None:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        self.ibg_port: int = _get_port(config["ib"]["account_type"])
        self.data_relevancy: int = config["ib"]["data_relevancy"]
        self.limit_MoE: float = config["ib"]["limit_MoE"]
        self.model: str = config["llm"]["model"]
        self.timeout: int = config["telegram"]["timeout"]
        self.openai_key: str | None = os.getenv("OPENAI_API_KEY")
        self.telegram_bot_key: str | None = os.getenv("TELEGRAM_BOT_KEY")


def _get_port(config: str) -> int:
    if config == "paper":
        return 4002
    if config == "live":
        return 4001
    else:
        raise NotImplementedError(f"No port assigned for: {config}")


config = Config("config.yaml")