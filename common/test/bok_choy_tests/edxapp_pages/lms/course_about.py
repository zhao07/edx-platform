from bok_choy.page_object import PageObject
from ..lms import BASE_URL


class CourseAboutPage(PageObject):
    """
    Course about page (with registration button)
    """

    @property
    def name(self):
        return "lms.course_about"

    def url(self, org=None, number=None, run=None):
        """
        URL for the about page of a course.
        `org`, `number`, and `run` are strings used to identify the course.
        """
        if org is None or number is None or run is None:
            raise NotImplemented("Must provide course identifiers to access about page")

        return BASE_URL + "/courses/{0}/{1}/{2}/about".format(org, number, run)

    def is_browser_on_page(self):
        return self.is_css_present('section.course-info')

    def register(self):
        """
        Register for the course on the page.
        """
        self.css_click('a.register')
        self.ui.wait_for_page('lms.register')
