# utils/enums.py

from enum import Enum


class InputAction(Enum):
    TRIGGER_PIPELINES = 'trigger_pipelines'
    CANCEL_BUILDS = 'cancel_builds'
    # Add other actions as needed

