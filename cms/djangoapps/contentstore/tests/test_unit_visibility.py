import json
import sys
from mock import Mock, patch
from django.test.utils import override_settings
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from xmodule.modulestore import Location
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.locator import BlockUsageLocator
from contentstore.tests.utils import parse_json, AjaxEnabledTestClient
from xmodule.modulestore.locator import BlockUsageLocator
from xmodule.modulestore.django import loc_mapper
from django.contrib.auth.models import User
from django.test.client import Client
from django.test.utils import override_settings


@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class TestUnitVisibility(ModuleStoreTestCase):
    """
    This test exercises the 'unit visibility' feature code. The feature is primarily visible when
    a course overview/outline view is opened in the Studio tool. The main functional elements are these:

        * Where units are shown on the page, one new visual element has been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the unit.

                The user may click on the icon to request a toggle of the public/private state. Before
                the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

        * Where subsections are shown on the page, two new visual elements have been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the units assigned to the subsection.
                Here there are three possible states for the icon to display: all units public, all units
                private, or a mix of the two.

                The user may click on the icon to request a change of state for all the assigned units. All
                public changes to all private (and vice versa). When there is a mix of public/private, the
                only available change is to make all units public.

                Before the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

            - A colored bar to the far left of the subsection's name
                This bar indicates the public/published state of the subsection. There are four possible
                states:
                    All public units and publication date > NOW
                    All public units and publication date < NOW
                    Some non-public units and publication date > NOW
                    Some non-public units and publication date < NOW

        * Where units are shown on the page, one new visual element has been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the units assigned to the section.
                Here there are three possible states for the icon to display: all units public, all units
                private, or a mix of the two.

                The user may click on the icon to request a toggle of the public/private state. Before
                the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

    The test situation for this test (established at setup time) is a simple course with only two sections, Dog and Cat.
    Each section has two subsections and each of those, in turn, have two units. This is the schematic representation
    of the course:

        Course
            Section: Dog
                Subsection: Best Friend
                    Unit_1a
                    Unit_1b
                Subsection: Loyal Companion
                    Unit_2a
                    Unit_2b

            Section: Cat
                Subsection: Aloof
                    Unit_3a
                    Unit_3b
                Subsection: Opportunistic Companion
                    Unit_4a
                    Unit_4b
    """
    def setUp(self):
        self.create_and_login_user()

        # ______________________________________ Course
        self.course = CourseFactory.create()
        print(str("\ncourse: " + str(self.course.location)))

        # ______________________________________ Sections
        self.section_dog = ItemFactory.create(
            parent_location=self.course.location,
            category="chapter",
            display_name="Dog",
        )
        print(str("\n    section_dog: " + str(self.section_dog.location)))

        self.section_cat = ItemFactory.create(
            parent_location=self.course.location,
            category="chapter",
            display_name="Cat",
        )
        print(str("\n    section_cat: " + str(self.section_cat.location)))

        # ______________________________________ Subsections
        self.sub_section_best_friend = ItemFactory.create(
            parent_location=self.section_dog.location,
            category="sequential",
            display_name="Best Friend",
        )
        print(str("\n        sub_section_best_friend: " + str(self.sub_section_best_friend.location)))

        self.sub_section_loyal_companion = ItemFactory.create(
            parent_location=self.section_dog.location,
            category="sequential",
            display_name="Loyal Companion",
        )
        print(str("\n        sub_section_loyal_companion: " + str(self.sub_section_loyal_companion.location)))

        self.sub_section_aloof = ItemFactory.create(
            parent_location=self.section_cat.location,
            category="sequential",
            display_name="Aloof",
        )
        print(str("\n        sub_section_aloof: " + str(self.sub_section_aloof.location)))

        self.sub_section_opportunistic_companion = ItemFactory.create(
            parent_location=self.section_cat.location,
            category="sequential",
            display_name="Opportunistic Companion",
        )
        print(str("\n        sub_section_opportunistic_companion: " + str(self.sub_section_opportunistic_companion.location)))

        # ______________________________________ Units
        self.unit_1a = ItemFactory.create(
            parent_location=self.sub_section_best_friend.location,
            category="vertical",
            display_name="Unit 1a",

        )
        print(str("\n                unit_1a: " + str(self.unit_1a.location)))

        self.unit_1b = ItemFactory.create(
            parent_location=self.sub_section_best_friend.location,
            category="vertical",
            display_name="Unit 1b",

        )
        print(str("\n                unit_1b: " + str(self.unit_1b.location)))

        self.unit_2a = ItemFactory.create(
            parent_location=self.sub_section_loyal_companion.location,
            category="vertical",
            display_name="Unit 2a",

        )
        print(str("\n                unit_2a: " + str(self.unit_2a.location)))

        self.unit_2b = ItemFactory.create(
            parent_location=self.sub_section_loyal_companion.location,
            category="vertical",
            display_name="Unit 2b",

        )
        print(str("\n                unit_2b: " + str(self.unit_2b.location)))

        self.unit_3a = ItemFactory.create(
            parent_location=self.sub_section_aloof.location,
            category="vertical",
            display_name="Unit 3a",

        )
        print(str("\n                unit_3a: " + str(self.unit_3a.location)))

        self.unit_3b = ItemFactory.create(
            parent_location=self.sub_section_aloof.location,
            category="vertical",
            display_name="Unit 3b",

        )
        print(str("\n                unit_3b: " + str(self.unit_3b.location)))

        self.unit_4a = ItemFactory.create(
            parent_location=self.sub_section_opportunistic_companion.location,
            category="vertical",
            display_name="Unit 4a",

        )
        print(str("\n                unit_4a: " + str(self.unit_4a.location)))

        self.unit_4b = ItemFactory.create(
            parent_location=self.sub_section_opportunistic_companion.location,
            category="vertical",
            display_name="Unit 4b",

        )
        print(str("\n                unit_4b: " + str(self.unit_4b.location)))

        print("\n\n")

    def create_and_login_user(self):
        uname = 'testuser'
        email = 'test+courses@edx.org'
        password = 'foo'

        self.user = User.objects.create_user(uname, email, password)
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client = AjaxEnabledTestClient()

        if self.client.login(username=uname, password=password):
            print 'Login successful: ' + uname
        else:
            print 'Login failed: ' + uname

    #def test_verify_test_course(self):
    #    '''
    #    Establish the test course has been created properly
    #    '''
    #    print('test_verify_test_course')
    #    from pdb import set_trace; set_trace()
    #    store = modulestore('direct')
    #
    #    # check the ancestry of each of the units
    #    unit_1a = store.get_item(self.unit_1a.location)
    #
    #
    #    self.assertEquals(1, 1)

    def test_get_html_response(self):
        store = modulestore('direct')
        descriptor = store.get_item(self.course.location)
        locator = loc_mapper().translate_location(self.course.location.course_id, descriptor.location, False, True)

        #url = locator.url()
        #url = 'edx://MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course'
        url = 'http://127.0.0.1:8001/course/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course'  # <<<< this works!

        response = self.client.get_html(url)
        #from pdb import set_trace; set_trace()
     #   response = self.client.get_html(locator.url_reverse('xblock'))
       # response = self.client.get_html(locator.url_reverse('unitstatus'))
       # response = self.client.get_html('http://127.0.0.1:8001/course/StanfordUniveristy.CS100.Fall2015/branch/draft/block/Fall2015')
        print '______________________________________________________ ' + url
        print response


