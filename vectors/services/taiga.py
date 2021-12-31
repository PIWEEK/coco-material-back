from django.conf import settings

from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException     # noqa


def create_suggestion(suggestion: str) -> None:
     api = TaigaAPI()
     api.auth(
         username=settings.TAIGA_USERNAME,
         password=settings.TAIGA_PASSWORD
     )

     project = api.projects.get_by_slug(settings.TAIGA_PROJECT_SLUG)
     project.add_issue(
         subject=suggestion,
         status=project.default_issue_status,
         issue_type=project.issue_types.get(name=settings.TAIGA_ISSUE_TYPE_NAME).id,
         priority=project.default_priority,
         severity=project.default_severity,
         description=suggestion,
         tags=["suggestion", "web"]
     )
