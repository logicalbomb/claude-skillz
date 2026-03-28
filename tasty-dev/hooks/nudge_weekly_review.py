# hooks/nudge_weekly_review.py
"""Hook to nudge for weekly project review"""
from pathlib import Path
from datetime import datetime, timedelta
import yaml
from typing import Optional, Dict

def check_review_needed(project_path: Path) -> Optional[Dict]:
    """Check if weekly review is needed"""
    config_path = project_path / ".tasty-dev" / "config.yaml"

    if not config_path.exists():
        return None

    with open(config_path) as f:
        config = yaml.safe_load(f)

    last_review = config.get("last_project_review")

    if last_review is None:
        # Never reviewed
        return {
            "days_since": None,
            "severity": "gentle",
            "message": "Consider running your first project review: /review-project"
        }

    last_review_date = datetime.fromisoformat(last_review)
    days_since = (datetime.now() - last_review_date).days

    if days_since >= 10:
        return {
            "days_since": days_since,
            "severity": "prominent",
            "message": f"Weekly review overdue by {days_since - 7} days. Run: /review-project"
        }
    elif days_since >= 7:
        return {
            "days_since": days_since,
            "severity": "gentle",
            "message": f"It's been {days_since} days since your last project review. Run: /review-project"
        }

    return None

def main():
    """Hook entry point"""
    # Called by Claude Code hook system
    # Event data passed via stdin or environment

    # For now, check current directory
    project_path = Path.cwd()
    result = check_review_needed(project_path)

    if result:
        print(result["message"])

if __name__ == "__main__":
    main()
