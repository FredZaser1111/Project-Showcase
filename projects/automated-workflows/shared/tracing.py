"""Lightweight tool/node tracing for agent demos (no external vendor required)."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Iterator


@dataclass
class TraceSpan:
    name: str
    case_id: str | None = None
    ok: bool = True
    latency_ms: float = 0.0
    detail: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


_SPANS: list[TraceSpan] = []


def reset_traces() -> None:
    _SPANS.clear()


def get_traces() -> list[dict[str, Any]]:
    return [asdict(s) for s in _SPANS]


@contextmanager
def trace_span(name: str, *, case_id: str | None = None, **detail: Any) -> Iterator[TraceSpan]:
    span = TraceSpan(name=name, case_id=case_id, detail=dict(detail))
    started = time.perf_counter()
    try:
        yield span
    except Exception as exc:  # noqa: BLE001 — capture then re-raise
        span.ok = False
        span.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        span.latency_ms = round((time.perf_counter() - started) * 1000, 2)
        _SPANS.append(span)
