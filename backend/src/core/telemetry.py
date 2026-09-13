"""Structured telemetry, correlation IDs, and OpenTelemetry logging."""
import logging
import uuid

logger = logging.getLogger("ai_design_studio")


def generate_trace_id() -> str:
    return str(uuid.uuid4())
