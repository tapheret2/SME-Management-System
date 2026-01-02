"""Utility functions."""


def sanitize_like(value: str) -> str:
    """Escape SQL LIKE wildcards to prevent injection."""
    if not value:
        return value
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
