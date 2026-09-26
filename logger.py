"""Безопасное журналирование результатов анализа."""

from datetime import datetime
import hashlib
from pathlib import Path


LOG_FILE = Path("security_log.txt")


def mask_sensitive_data(text: str) -> str:
    """Возвращает безопасный идентификатор, не сохраняя исходный текст."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"[текст скрыт; символов: {len(text)}; SHA-256: {digest}]"


def write_log(text: str, decisions) -> None:
    statuses = ", ".join(sorted({decision.status for decision in decisions}))
    laws = "; ".join(sorted({decision.law for decision in decisions}))
    masked = mask_sensitive_data(text)
    line = f"{datetime.now().isoformat(timespec='seconds')} | {statuses} | {laws} | {masked}\n"
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line)
