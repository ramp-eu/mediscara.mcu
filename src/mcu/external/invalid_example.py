
from typing import List
from mcu.models.user_defined import Command


class InvalidCommand(Command):
    # this should not take any arguments
    def __init__(self, keywords: str | List[str]) -> None:
        super().__init__(keywords)

    def target(self, *args, keyword: str):
        return super().target(*args, keyword=keyword)
