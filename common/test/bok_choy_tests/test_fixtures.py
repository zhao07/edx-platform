"""
Very simple test case to verify bok-choy integration.
"""

from bok_choy.web_app_test import WebAppTest
from .edxapp_pages.lms.info import InfoPage

from .fixtures.course import XBlockFixtureDesc, CourseFixture


class CoursePageTest(WebAppTest):
    """
    Test that the top-level pages in the LMS load.
    """

    @property
    def page_object_classes(self):
        return [InfoPage]

    @property
    def fixtures(self):
        fix = CourseFixture('edx', '999', 'Spring_2014', 'Test Course', [
            XBlockFixtureDesc('chapter', 'Test Section', children=[
                XBlockFixtureDesc('sequential', 'Test Subsection', children=[
                    XBlockFixtureDesc('html', 'Test HTML 1'),
                    XBlockFixtureDesc('html', 'Test HTML 2')
                ])
            ])
        ])
        return [fix]

    def test_course(self):
        for section_name in InfoPage.sections():
            self.ui.visit('lms.info', section=section_name)
