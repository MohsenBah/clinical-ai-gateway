from dataclasses import dataclass


@dataclass
class OutputFilterResult:
    safe_text: str
    modified: bool = False
    reason: str = "allowed"


def filter_output(text: str) -> OutputFilterResult:
    # Placeholder for future PHI filtering with Microsoft Presidio.
    return OutputFilterResult(safe_text=text)
