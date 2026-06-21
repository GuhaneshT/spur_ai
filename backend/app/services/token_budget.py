from app.core.config import get_settings


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def enforce_daily_budget(current_tokens: int, incoming_text: str) -> None:
    settings = get_settings()
    if current_tokens + estimate_tokens(incoming_text) > settings.daily_token_budget_per_session:
        raise ValueError("Daily session token budget exceeded.")
