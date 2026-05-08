import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("audit")


def audit_log(**fields: Any) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    logger.info(json.dumps(event, ensure_ascii=False))
