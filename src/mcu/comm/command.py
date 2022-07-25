"""Model for a single command"""
from dataclasses import dataclass, field

@dataclass
class Command:
    keyword: str = field()
