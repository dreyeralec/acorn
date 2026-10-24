import yaml
import os

from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel, Field

_ = load_dotenv()


@dataclass
class WakeUpEvent(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    second: int = Field(ge=0, le=59)
    type: Literal["trade", "analysis"]


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
        self.wake_up_events: list[WakeUpEvent] = _build_wake_up_events(config["engine"]["wake_ups"])


def _get_port(acc_type: str) -> int:
    if acc_type == "paper":
        return 4002
    if acc_type == "live":
        return 4001
    else:
        raise NotImplementedError(f"No port assigned for: {acc_type}")


def _build_wake_up_events(config: list[dict[str, object]]) -> list[WakeUpEvent]:
    return [WakeUpEvent.model_validate(event) for event in config]


config = Config("config.yaml")