from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FileFingerprint:
    path: str
    name: str
    size_bytes: int
    sha256: str
    modified_at_utc: str

    def to_dict(self) -> dict:
        return asdict(self)


def fingerprint_files(paths: Iterable[str | Path]) -> list[dict]:
    return [fingerprint_file(path).to_dict() for path in sorted(Path(item) for item in paths)]


def fingerprint_file(path: str | Path) -> FileFingerprint:
    file_path = Path(path)
    stat = file_path.stat()
    return FileFingerprint(
        path=str(file_path),
        name=file_path.name,
        size_bytes=stat.st_size,
        sha256=_sha256(file_path),
        modified_at_utc=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat(),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
