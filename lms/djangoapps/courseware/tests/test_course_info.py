"""
Test the course_info xblock
"""
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from .helpers import LoginEnrollmentTestCase
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class CourseInfoTestCase(LoginEnrollmentTestCase, ModuleStoreTestCase):
    def setUp(self):
        self.course = CourseFactory.create()
        self.page = ItemFactory.create(
            category="course_info", parent_location=self.course.location,
            data="OOGIE BLOOGIE", display_name="updates"
        )
        self.xml_data = "course info 463139"
        self.xml_course_id = 'edX/detached_pages/2014'
        self.params = [
            (self.course.id, "OOGIE BLOOGIE"),
            (self.xml_course_id, self.xml_data)
        ]

    def test_logged_in(self):
        self.setup_user()
        for course_id, data in self.params:
            url = reverse('info', args=[course_id])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(data, resp.content)

    def test_anonymous_user(self):
        for course_id, data in self.params:
            url = reverse('info', args=[course_id])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(data, resp.content)
