import os
import yaml
import logging
from dataclasses import dataclass
from typing import Literal

def load_config(config_path):
    if os.path.isdir(config_path):
        config_path = os.path.join(config_path, "config.yml")
    logging.info(f"load config from path: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    config = Config.from_yaml(config_data)
    return config

@dataclass
class Config:
    # appium server config
    appium_server_host: str

    # locate model config
    locate_model_type: Literal["local", "remote"]
    locate_model_host: str

    # validate model config
    validate_model_type: Literal["local", "remote"]
    validate_model_host: str

    # device config
    device_type: Literal["android", "ios"]
    # is not necessary in config.yml, appium can auto get device width and height
    device_width: int
    device_height: int

    # app config
    app_package: str
    app_activity: str

    @classmethod
    def from_yaml(cls, yaml_data: dict) -> "Config":
        return cls(
            appium_server_host=yaml_data.get("appium-server-host", ""),
            locate_model_type=yaml_data.get("locate-model-type", "local"),
            locate_model_host=yaml_data.get("locate-model-host", ""),
            validate_model_type=yaml_data.get("validate-model-type", "local"),
            validate_model_host=yaml_data.get("validate-model-host", ""),
            device_type=yaml_data.get("device-type", ""),
            device_width=yaml_data.get("device-width", 0),
            device_height=yaml_data.get("device-height", 0),
            app_package=yaml_data.get("app-package", ""),
            app_activity=yaml_data.get("app-activity", "")
        )
