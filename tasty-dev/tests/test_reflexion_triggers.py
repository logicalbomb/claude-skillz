# tests/test_reflexion_triggers.py
import pytest
from hooks.detect_reflexion_triggers import (
    detect_trigger,
    TriggerType,
    TriggerEvent
)

def test_detect_human_deliberation():
    """Detects human deliberation in user messages"""
    user_message = "Actually, I think we should use PostgreSQL instead"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is not None
    assert trigger.type == TriggerType.HUMAN_DELIBERATION
    assert "PostgreSQL" in trigger.context

def test_detect_test_failure():
    """Detects test failures in tool results"""
    tool_result = {
        "tool": "Bash",
        "command": "pytest tests/",
        "output": "FAILED tests/test_api.py::test_endpoint",
        "exit_code": 1
    }
    trigger = detect_trigger("tool_result", tool_result)

    assert trigger is not None
    assert trigger.type == TriggerType.SYSTEM_FAILURE
    assert "test_endpoint" in trigger.context

def test_no_trigger_for_simple_acceptance():
    """No trigger for simple acceptance messages"""
    user_message = "Great, thanks!"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is None

def test_detect_design_conflict():
    """Detects conflicts with existing ADRs"""
    user_message = "Wait, that conflicts with our decision to use REST"
    trigger = detect_trigger("user_message", {"content": user_message})

    assert trigger is not None
    assert trigger.type == TriggerType.DESIGN_CONFLICT
