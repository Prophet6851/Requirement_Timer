from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    module: str = ""
    version: str = ""
    status: str = ""
    priority: str = ""
    plan_start: str = ""   # yyyy-mm-dd
    plan_end: str = ""     # yyyy-mm-dd
    notes: str = ""