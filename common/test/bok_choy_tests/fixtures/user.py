"""
Fixtures to create users for tests.
"""

from .base import DjangoCmdFixture
from bok_choy.web_app_fixture import WebAppFixture


class StudentUserFixture(DjangoCmdFixture):
    """
    Create a student user, optionally enrolled in a course.
    """

    def __init__(self, username, password, email, course_id=None, enrollment='honor'):
        """
        Configure the fixture to create a student with `username`, `password`,
        and `email` if the student does not already exist.
        If `course_id` is specified, ensure that the user is registered for the course.

        `enrollment` can be either 'audit', 'verified', or 'honor'.

        Example:

            StudentUserFixture('foo', 'password', 'foo@example.com', course='edx/101/Spring_2014', enrollment='audit')
        """
        kwargs = {
            'username': username,
            'password': password,
            'email': email,
            'mode': enrollment
        }

        if course_id is not None:
            self.kwargs['course'] = course_id

        super(StudentUserFixture, self).__init__('create_user', **kwargs)


class StaffUserFixture(DjangoCmdFixture):
    """
    Create a user with global staff permissions.

    Note that "staff" in this context is NOT the same as "course staff".
    The "staff" bit is set for site administrators, not course teams.
    """

    def __init__(self, username, password, email, course_id=None):
        """
        Configure the fixture to Create a student with `username`, `password`,
        and `email` if the student does not already exist.
        If `course_id` is specified, ensure that the user is registered for the course.

        `enrollment` can be either 'audit', 'verified', or 'honor'.

        Example:

            StudentUserFixture('foo', 'password', 'foo@example.com', course='edx/101/Spring_2014', enrollment='audit')
        """

        kwargs = {
            'username': username,
            'password': password,
            'email': email,
            'staff': True
        }

        if course_id is not None:
            self.kwargs['course'] = course_id

        super(StaffUserFixture, self).__init__('create_user', **kwargs)
