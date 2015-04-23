"""
Discussion API views
"""
from django.http import Http404

from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.exceptions import MethodNotAllowed, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from opaque_keys.edx.locator import CourseLocator

from courseware.courses import get_course_with_access
from discussion_api.api import get_course_topics
from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin


def _make_error_response(status_code, developer_message):
    """
    Return an error response with the given status code and developer
    message
    """
    return Response({"developer_message": developer_message}, status=status_code)


class CourseTopicsView(DeveloperErrorViewMixin, APIView):
    """
    **Use Cases**

        Retrieve the topic listing for a course. Only topics accessible to the
        authenticated user are included.

    **Example Requests**:

        GET /api/discussion/v1/course_topics/{course_id}

    **Response Values**:

        * courseware_topics: The list of topic trees for courseware-linked
          topics. Each item in the list includes:

            * id: The id of the discussion topic (null for a topic that only
              has children but cannot contain threads itself).

            * name: The display name of the topic.

            * thread_list_url: The URL from which the list of threads in the
              topic can be retrieved.

            * children: A list of child subtrees of the same format.

        * non_courseware_topics: The list of topic trees that are not linked to
              courseware. Items are of the same format as in courseware_topics.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, course_id):
        course_key = CourseLocator.from_string(course_id)
        course = get_course_with_access(request.user, 'load_forum', course_key)
        return Response(get_course_topics(course, request.user, request.build_absolute_uri))
