"""
Private utilities.
"""
import os
from typing import Mapping, Any, Optional, Callable, cast

import pyramid.config


def get_base_path(config: pyramid.config.Configurator) -> str:
    return cast(str, env_or_config(config, 'C2C_BASE_PATH', 'c2c.base_path', '/c2c'))


def env_or_config(
        config: Optional[pyramid.config.Configurator],
        env_name: Optional[str] = None, config_name: Optional[str] = None,
        default: Any = None, type_: Callable[[str], Any] = str) -> Any:
    return env_or_settings(
        config.get_settings() if config is not None else {}, env_name, config_name, default, type_)


def env_or_settings(
        settings: Optional[Mapping[str, Any]],
        env_name: Optional[str] = None, settings_name: Optional[str] = None,
        default: Any = None, type_: Callable[[str], Any] = str) -> Any:
    if env_name is not None and env_name in os.environ:
        return type_(os.environ[env_name])
    if settings is not None and settings_name is not None and settings_name in settings:
        return type_(settings[settings_name])
    return default


def config_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.lower() in ('true', 't', 'yes', '1')
