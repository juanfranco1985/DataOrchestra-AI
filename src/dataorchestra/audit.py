from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    event: str
    client_id: str
    status: str
    details: dict[str, Any]
    created_at: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_audit_event(log_path: str | Path, event: str, client_id: str, status: str, details: dict[str, Any]) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = AuditEvent(event=event, client_id=client_id, status=status, details=details, created_at=now_iso())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(payload), ensure_ascii=False) + "\n")
