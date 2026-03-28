# hooks/detect_reflexion_triggers.py
"""Detect reflexion triggers from user messages and tool results"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re

class TriggerType(Enum):
    HUMAN_DELIBERATION = "human_deliberation"
    SYSTEM_FAILURE = "system_failure"
    DESIGN_CONFLICT = "design_conflict"
    REPEATED_FRICTION = "repeated_friction"
    USER_INVOCATION = "user_invocation"

@dataclass
class TriggerEvent:
    type: TriggerType
    context: str
    severity: str  # "major" or "minor"

# Patterns for human deliberation
DELIBERATION_PATTERNS = [
    r"\b(actually|instead|rather|alternatively)\b",
    r"\b(think|consider|prefer|suggest)\b.*\b(should|could|might)\b",
    r"\b(what about|how about|why not)\b",
    r"\b(but|however|although)\b",
    r"\b(option|alternative|approach)\b",
]

# Patterns for design conflicts
CONFLICT_PATTERNS = [
    r"\b(conflict|contradicts?|violates?)\b",
    r"\b(against|breaks|challenges)\b.*\b(decision|ADR|architecture)\b",
    r"\bwait\b.*\b(that|this)\b",
]

def detect_trigger(event_type: str, event_data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect if event should trigger reflexion"""

    if event_type == "user_message":
        return _detect_user_message_trigger(event_data)
    elif event_type == "tool_result":
        return _detect_tool_result_trigger(event_data)

    return None

def _detect_user_message_trigger(data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect triggers in user messages"""
    content = data.get("content", "")
    content_lower = content.lower()

    # Skip simple acceptance messages
    if re.match(r"^(ok|okay|great|thanks|sure|yes|yep|yeah)[\s!.]*$", content_lower):
        return None

    # Check for explicit commands
    if re.match(r"/(reflect|correct)", content_lower):
        return TriggerEvent(
            type=TriggerType.USER_INVOCATION,
            context=content,
            severity="major"
        )

    # Check for design conflicts
    for pattern in CONFLICT_PATTERNS:
        if re.search(pattern, content_lower):
            return TriggerEvent(
                type=TriggerType.DESIGN_CONFLICT,
                context=content,
                severity="major"
            )

    # Check for deliberation
    for pattern in DELIBERATION_PATTERNS:
        if re.search(pattern, content_lower):
            return TriggerEvent(
                type=TriggerType.HUMAN_DELIBERATION,
                context=content,
                severity="minor"
            )

    return None

def _detect_tool_result_trigger(data: Dict[str, Any]) -> Optional[TriggerEvent]:
    """Detect triggers in tool results"""
    tool = data.get("tool", "")
    output = data.get("output", "")
    output_lower = output.lower()
    exit_code = data.get("exit_code", 0)

    # Test failures
    if tool == "Bash" and exit_code != 0:
        if any(word in output_lower for word in ["failed", "error", "failure"]):
            return TriggerEvent(
                type=TriggerType.SYSTEM_FAILURE,
                context=output[:200],
                severity="major"
            )

    return None
