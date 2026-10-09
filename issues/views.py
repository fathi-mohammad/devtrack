import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from issues.models import Issue, Reporter, build_issue
from issues.storage import issues_store, reporters_store


def parse_body(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"error": "Invalid JSON body"}, status=400)
    if not isinstance(data, dict):
        return None, JsonResponse({"error": "Body must be a JSON object"}, status=400)
    return data, None


def parse_id(raw):
    try:
        return int(raw), None
    except (TypeError, ValueError):
        return None, JsonResponse({"error": "id must be an integer"}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def reporters(request):
    if request.method == "POST":
        return create_reporter(request)

    raw_id = request.GET.get("id")
    if raw_id is None:
        return JsonResponse(reporters_store.all(), safe=False, status=200)

    reporter_id, error = parse_id(raw_id)
    if error:
        return error
    reporter = reporters_store.get(reporter_id)
    if reporter is None:
        return JsonResponse({"error": "Reporter not found"}, status=404)
    return JsonResponse(reporter, status=200)


def create_reporter(request):
    data, error = parse_body(request)
    if error:
        return error

    reporter = Reporter(
        id=data.get("id"),
        name=data.get("name"),
        email=data.get("email"),
        team=data.get("team"),
    )
    try:
        reporter.validate()
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if reporters_store.get(reporter.id):
        return JsonResponse({"error": f"Reporter with id {reporter.id} already exists"}, status=409)

    reporters_store.add(reporter.to_dict())
    return JsonResponse(reporter.to_dict(), status=201)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def issues(request):
    if request.method == "POST":
        return create_issue(request)

    raw_id = request.GET.get("id")
    status = request.GET.get("status")

    if raw_id is not None:
        issue_id, error = parse_id(raw_id)
        if error:
            return error
        issue = issues_store.get(issue_id)
        if issue is None:
            return JsonResponse({"error": "Issue not found"}, status=404)
        return JsonResponse(issue, status=200)

    if status is not None:
        if status not in Issue.VALID_STATUSES:
            return JsonResponse(
                {"error": f"Invalid status. Allowed: {', '.join(Issue.VALID_STATUSES)}"},
                status=400,
            )
        return JsonResponse(issues_store.filter(status=status), safe=False, status=200)

    return JsonResponse(issues_store.all(), safe=False, status=200)


def create_issue(request):
    data, error = parse_body(request)
    if error:
        return error

    issue = build_issue(data)
    try:
        issue.validate()
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if issues_store.get(issue.id):
        return JsonResponse({"error": f"Issue with id {issue.id} already exists"}, status=409)
    if reporters_store.get(issue.reporter_id) is None:
        return JsonResponse({"error": "Reporter not found"}, status=404)

    issues_store.add(issue.to_dict())
    response_data = issue.to_dict()
    response_data["message"] = issue.describe()
    return JsonResponse(response_data, status=201)
