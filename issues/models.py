from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not isinstance(self.id, int):
            raise ValueError("id must be an integer")
        if not self.name or not str(self.name).strip():
            raise ValueError("Name cannot be empty")
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email")
        if not self.team:
            raise ValueError("Team cannot be empty")


class Issue(BaseEntity):
    VALID_STATUSES = ("open", "in_progress", "resolved", "closed")
    VALID_PRIORITIES = ("low", "medium", "high", "critical")

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = created_at or str(datetime.now())

    def validate(self):
        if not isinstance(self.id, int):
            raise ValueError("id must be an integer")
        if not self.title or not str(self.title).strip():
            raise ValueError("Title cannot be empty")
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Allowed: {', '.join(self.VALID_STATUSES)}")
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority. Allowed: {', '.join(self.VALID_PRIORITIES)}")
        if not isinstance(self.reporter_id, int):
            raise ValueError("reporter_id must be an integer")

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} — low priority, handle when free"


def build_issue(data):
    issue_cls = {"critical": CriticalIssue, "low": LowPriorityIssue}.get(data.get("priority"), Issue)
    return issue_cls(
        id=data.get("id"),
        title=data.get("title"),
        description=data.get("description", ""),
        status=data.get("status"),
        priority=data.get("priority"),
        reporter_id=data.get("reporter_id"),
    )
