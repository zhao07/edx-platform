"""
Test the about xblock
"""
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from .helpers import LoginEnrollmentTestCase
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class AboutTestCase(LoginEnrollmentTestCase, ModuleStoreTestCase):
    def setUp(self):
        self.course = CourseFactory.create()
        self.about = ItemFactory.create(
            category="about", parent_location=self.course.location,
            data="OOGIE BLOOGIE", display_name="overview"
        )
        self.xml_data = "about page 463139"
        self.xml_course_id = 'edX/detached_pages/2014'
        self.params = [
            (self.course.id, "OOGIE BLOOGIE"),
            (self.xml_course_id, self.xml_data)
        ]


    def test_logged_in(self):
        self.setup_user()
        for course_id, data in self.params:
            url = reverse('about_course', args=[course_id])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(data, resp.content)

    def test_anonymous_user(self):
        for course_id, data in self.params:
            url = reverse('about_course', args=[course_id])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(data, resp.content)
