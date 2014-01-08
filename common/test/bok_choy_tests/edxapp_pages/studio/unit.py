from bok_choy.page_object import PageObject
from ..studio import BASE_URL


class UnitPage(PageObject):
    """
    Unit page in Studio
    """

    @property
    def name(self):
        return "studio.unit"

    def url(self):
        raise NotImplemented

    def is_browser_on_page(self):
        return self.is_css_present('body.view-unit')
