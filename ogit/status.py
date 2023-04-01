from dataclasses import dataclass

@dataclass
class Status:
    untracked: list[str]
    unstaged: list[str]
