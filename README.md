# DevTrack

A minimal Django backend for tracking engineering issues — a stripped-down GitHub Issues. Data lives in `issues.json` and `reporters.json`; the domain is modelled with plain Python OOP classes in `issues/models.py`.

## Run

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

API base: `http://127.0.0.1:8000/api/`

The JSON files are created automatically on first run if missing. Import `DevTrack.postman_collection.json` into Postman to get every request pre-built.

## Endpoints

### Reporters

| Method | URL | Description | Responses |
|---|---|---|---|
| POST | `/api/reporters/` | Create a reporter | 201, 400 (validation), 409 (duplicate id) |
| GET | `/api/reporters/` | List all reporters | 200 |
| GET | `/api/reporters/?id=1` | Get one reporter | 200, 404, 400 (non-integer id) |

```json
{ "id": 1, "name": "Asha Nair", "email": "asha@devtrack.io", "team": "backend" }
```

### Issues

| Method | URL | Description | Responses |
|---|---|---|---|
| POST | `/api/issues/` | Create an issue | 201, 400 (validation), 404 (unknown reporter), 409 (duplicate id) |
| GET | `/api/issues/` | List all issues | 200 |
| GET | `/api/issues/?id=1` | Get one issue | 200, 404, 400 (non-integer id) |
| GET | `/api/issues/?status=open` | Filter by status | 200, 400 (invalid status) |

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

Response `201`:

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1,
  "created_at": "2026-10-09 19:44:14.182518",
  "message": "[URGENT] Login button not working on mobile — needs immediate attention"
}
```

Allowed values — `status`: `open`, `in_progress`, `resolved`, `closed` · `priority`: `low`, `medium`, `high`, `critical`.

Errors always come back as `{ "error": "<reason>" }`.

## OOP design

```
BaseEntity (ABC)          validate() abstract, to_dict() shared
├── Reporter
└── Issue                 describe() -> "title [priority]"
    ├── CriticalIssue     describe() -> "[URGENT] ..."
    └── LowPriorityIssue  describe() -> "... low priority, handle when free"
```

`build_issue(data)` picks the subclass from `priority` (critical → `CriticalIssue`, low → `LowPriorityIssue`, else `Issue`), so the view just calls `validate()`, `to_dict()` and `describe()` polymorphically.

## Design decisions

**Storage behind a `JsonStore` class (`issues/storage.py`).** Views never open files directly; they call `all()`, `get(id)`, `filter(**criteria)` and `add(record)`. This keeps file I/O in one place, removes duplicated read/loop/match code across endpoints, and means swapping JSON for a real database later only touches the store, not the views or models.

Also:
- **Referential integrity on create** — an issue is rejected with 404 if its `reporter_id` doesn't exist, enforcing the 1:many relationship instead of trusting the client.
- **Subclass selection lives in `models.py`** (`build_issue`), so the view doesn't need an if/elif chain and new priority types only require a new subclass + one mapping entry.
- **409 on duplicate ids** so records can't silently collide.
- **CSRF exempt** on API views since this is a token-less JSON API tested from Postman.

## Postman screenshots

Add your screenshots to `screenshots/` and they will render here.

| Case | Screenshot |
|---|---|
| POST `/api/issues/` — 201 Created | ![success](screenshots/create_issue_success.png) |
| POST `/api/issues/` — 400 empty title | ![failure](screenshots/create_issue_failure.png) |
| GET `/api/issues/?id=42` — 404 | ![not found](screenshots/get_issue_not_found.png) |

## Structure

```
devtrack/
├── manage.py
├── requirements.txt
├── issues.json
├── reporters.json
├── DevTrack.postman_collection.json
├── devtrack/
│   ├── settings.py
│   └── urls.py
└── issues/
    ├── models.py
    ├── storage.py
    ├── views.py
    └── urls.py
```
