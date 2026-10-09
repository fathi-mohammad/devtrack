import json
from pathlib import Path

from django.conf import settings

DATA_DIR = Path(settings.BASE_DIR)


class JsonStore:
    def __init__(self, filename):
        self.path = DATA_DIR / filename
        if not self.path.exists():
            self.path.write_text("[]")

    def all(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def get(self, record_id):
        return next((r for r in self.all() if r["id"] == record_id), None)

    def filter(self, **criteria):
        return [r for r in self.all() if all(r.get(k) == v for k, v in criteria.items())]

    def add(self, record):
        records = self.all()
        records.append(record)
        with open(self.path, "w") as f:
            json.dump(records, f, indent=2)


issues_store = JsonStore("issues.json")
reporters_store = JsonStore("reporters.json")
