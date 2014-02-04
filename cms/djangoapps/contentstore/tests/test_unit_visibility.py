import json
import sys
import re

#import lxml.html
from lxml import etree


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
        self._create_and_login_user()

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

        #self.sub_section_loyal_companion = ItemFactory.create(
        #    parent_location=self.section_dog.location,
        #    category="sequential",
        #    display_name="Loyal Companion",
        #)
        #print(str("\n        sub_section_loyal_companion: " + str(self.sub_section_loyal_companion.location)))
        #
        #self.sub_section_aloof = ItemFactory.create(
        #    parent_location=self.section_cat.location,
        #    category="sequential",
        #    display_name="Aloof",
        #)
        #print(str("\n        sub_section_aloof: " + str(self.sub_section_aloof.location)))
        #
        #self.sub_section_opportunistic_companion = ItemFactory.create(
        #    parent_location=self.section_cat.location,
        #    category="sequential",
        #    display_name="Opportunistic Companion",
        #)
        #print(str("\n        sub_section_opportunistic_companion: " + str(self.sub_section_opportunistic_companion.location)))

        # ______________________________________ Units
        self.unit_1a = ItemFactory.create(
            parent_location=self.sub_section_best_friend.location,
            category="vertical",
            display_name="Unit 1a",

        )
        print(str("\n                unit_1a: " + str(self.unit_1a.location)))

        #self.unit_1b = ItemFactory.create(
        #    parent_location=self.sub_section_best_friend.location,
        #    category="vertical",
        #    display_name="Unit 1b",
        #
        #)
        #print(str("\n                unit_1b: " + str(self.unit_1b.location)))
        #
        #self.unit_2a = ItemFactory.create(
        #    parent_location=self.sub_section_loyal_companion.location,
        #    category="vertical",
        #    display_name="Unit 2a",
        #
        #)
        #print(str("\n                unit_2a: " + str(self.unit_2a.location)))
        #
        #self.unit_2b = ItemFactory.create(
        #    parent_location=self.sub_section_loyal_companion.location,
        #    category="vertical",
        #    display_name="Unit 2b",
        #
        #)
        #print(str("\n                unit_2b: " + str(self.unit_2b.location)))
        #
        #self.unit_3a = ItemFactory.create(
        #    parent_location=self.sub_section_aloof.location,
        #    category="vertical",
        #    display_name="Unit 3a",
        #
        #)
        #print(str("\n                unit_3a: " + str(self.unit_3a.location)))
        #
        #self.unit_3b = ItemFactory.create(
        #    parent_location=self.sub_section_aloof.location,
        #    category="vertical",
        #    display_name="Unit 3b",
        #
        #)
        #print(str("\n                unit_3b: " + str(self.unit_3b.location)))
        #
        #self.unit_4a = ItemFactory.create(
        #    parent_location=self.sub_section_opportunistic_companion.location,
        #    category="vertical",
        #    display_name="Unit 4a",
        #
        #)
        #print(str("\n                unit_4a: " + str(self.unit_4a.location)))
        #
        #self.unit_4b = ItemFactory.create(
        #    parent_location=self.sub_section_opportunistic_companion.location,
        #    category="vertical",
        #    display_name="Unit 4b",
        #
        #)
        #print(str("\n                unit_4b: " + str(self.unit_4b.location)))
        #print("\n\n")

        self._get_html_response()

    def _create_and_login_user(self):
        '''
        Create a test user and log the new user into the system
        '''
        uname = 'testuser'
        email = 'test+courses@edx.org'
        password = 'foo'

        self.user = User.objects.create_user(uname, email, password)
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client = AjaxEnabledTestClient()
        self.assertTrue(self.client.login(username=uname, password=password), 'Login failed: ' + uname)

    def _get_html_response(self):
        '''
        Request the Studio outline view of the course and save the html to a local variable for testing
        '''
        store = modulestore('direct')
        descriptor = store.get_item(self.course.location)
        locator = loc_mapper().translate_location(self.course.location.course_id, descriptor.location, False, True)
        url = locator.url().replace('edx:/', 'http://127.0.0.1:8001/course')

        self.outline_view_html = self.client.get_html(url)                  # save the html response for reference
        #from pdb import set_trace; set_trace()
        print self.outline_view_html

        self.outline_view_xml = etree.fromstring(self.outline_view_html.content)    # generate an XPath-able XML version too
        #e = self.outline_view_xml  # dummy

    def _assert_match(self, match_pattern, error_announcement_message='No regex match found'):
        '''
        Try to match the regex pattern supplied against the html saved locally. If the pattern cannot be matched,
        issue an exception via the testing framework's assert functionality
        '''
        decorated_announcement = "\n\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + error_announcement_message + "\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> (pattern: " + match_pattern + ")\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        matchObj = re.search(match_pattern, str(self.outline_view_html))
        self.assertFalse(matchObj is None, decorated_announcement)

    def _assert_xpath(self, xpath, error_announcement_message='XPath did not yield an element'):
        '''
        Execute the Xpath query against the xml saved locally. If the query fails,
        issue an exception via the testing framework's assert functionality
        '''
        decorated_announcement = "\n\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + error_announcement_message + "\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> (xpath: " + xpath + ")\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        decorated_announcement += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        self.assertTrue(self.outline_view_xml.xpath(xpath), decorated_announcement)

    def test_verify_course_outline(self):
        '''
        Verify the structure of the testcase course matches what the tests are expecting.
        '''

        # Check for properly constructed Sections
        self._assert_xpath('/html/body/div/div/div/section/article/div/article/section/header/div/h3/@data-name="Dog"', 'No section named "Dog"')
        self._assert_xpath('/html/body/div/div/div/section/article/div/article/section/header/div/h3/@data-name="Cat"', 'No section named "Cat"')

        # Check for properly constructed Subsections
        self._assert_xpath('/html/body/div/div/div/section/article/div/article/section/header/div/h3/@data-name="Cat"', 'No section named "Cat"')




#    massaged_html =     '''
#
#    <html>
#        <!--<![endif]-->
#        <head>
#
#
#            <title> Course Outline | Robot Super Course | edX Studio </title>
#
#
#
#            <link href="css/cms-style-vendor.css" rel="stylesheet" type="text/css" />
#
#
#
#
#            <link href="css/cms-style-app.css" rel="stylesheet" type="text/css" />
#
#
#
#
#            <link href="css/cms-style-app-extend1.css" rel="stylesheet" type="text/css" />
#
#
#
#
#            <link href="css/cms-style-xmodule.css" rel="stylesheet" type="text/css" />
#
#
#
#
#
#
#
#
#            <!-- dummy segment.io -->
#            <script type="text/javascript">
#  var course_location_analytics = "MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course";
#  var analytics = {
#    "track": function() {}
#  };
#</script>
#            <!-- end dummy segment.io -->
#
#
#
#            <script type="text/template" id="new-section-template">
#    <section class="courseware-section new-section is-collapsible is-draggable">
#      <header class="section">
#      <a href="#" data-tooltip="Expand/collapse this section" class="action expand-collapse collapse"><i class="icon-caret-down ui-toggle-expansion"></i><span class="sr">Expand/collapse this section</span></a>
#        <div class="item-details">
#          <h3 class="section-name">
#            <form class="section-name-form">
#              <input type="text" value="New Section Name" class="new-section-name" />
#              <input type="submit" class="new-section-name-save" data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course" data-category="chapter" value="Save" />
#              <input type="button" class="new-section-name-cancel" value="Cancel" />
#            </form>
#          </h3>
#        </div>
#      </header>
#    </section>
#  </script>
#
#
#            <script type="text/template" id="blank-slate-template">
#  <section class="courseware-section new-section">
#    <header>
#      <a href="#" data-tooltip="Expand/collapse this section" class="action expand-collapse"><i class="icon-caret-down ui-toggle-dd"></i><span class="sr">Expand/collapse this section</span></a>
#      <div class="item-details">
#        <h3 class="section-name">
#        <span class="section-name-span">Add a new section name</span>
#        <form class="section-name-form">
#          <input type="text" value="New Section Name" class="new-section-name" />
#          <input type="submit" class="new-section-name-save" data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course" data-category="chapter" value="Save" />
#          <input type="button" class="new-section-name-cancel" value="$(_('Cancel')}" />
#        </form></h3>
#      </div>
#      <div class="item-actions">
#        <a href="#" data-tooltip="Delete this section" class="delete-button delete-section-button"><span class="delete-icon"></span></a>
#        <span data-tooltip="Drag to re-order" class="drag-handle"></span>
#      </div>
#    </header>
#  </section>
#  </script>
#
#            <script type="text/template" id="new-subsection-template">
#  <li class="courseware-subsection collapsed is-draggable is-collapsible">
#    <div class="section-item editing">
#      <form class="new-subsection-form">
#        <span class="subsection-name">
#          <input type="text" value="New Subsection" class="new-subsection-name-input" />
#        </span>
#        <input type="submit" value="Save" class="new-subsection-name-save" />
#        <input type="button" value="Cancel" class="new-subsection-name-cancel" />
#      </form>
#    </div>
#    <ol>
#      <li>
#        <a href="unit.html" class="new-unit-item">
#          <i class="icon-plus"></i> New Unit
#        </a>
#      </li>
#    </ol>
#  </li>
#  </script>
#
#            <script type="text/template" id="no-outline-content">
#  <div class="no-outline-content">
#      <p>You haven't added any sections to your course outline yet. <a href="#" class="button new-button"><i class="icon-plus"></i>Add your first section</a></p>
#  </div>
#  </script>
#
#        </head>
#
#        <body class="is-signedin course view-outline feature-edit-dialog hide-wip">
#            <a class="nav-skip" href="#content">Skip to this view's content</a>
#
#            <script type="text/javascript">
#    window.baseUrl = "/static/89e9847/";
#    var require = {
#        baseUrl: baseUrl,
#        waitSeconds: 60,
#        paths: {
#            "domReady": "js/vendor/domReady",
#            "gettext": "/i18n",
#            "mustache": "js/vendor/mustache",
#            "codemirror": "js/vendor/codemirror-compressed",
#            "codemirror/stex": "js/vendor/CodeMirror/stex",
#            "jquery": "js/vendor/jquery.min",
#            "jquery.ui": "js/vendor/jquery-ui.min",
#            "jquery.form": "js/vendor/jquery.form",
#            "jquery.markitup": "js/vendor/markitup/jquery.markitup",
#            "jquery.leanModal": "js/vendor/jquery.leanModal.min",
#            "jquery.ajaxQueue": "js/vendor/jquery.ajaxQueue",
#            "jquery.smoothScroll": "js/vendor/jquery.smooth-scroll.min",
#            "jquery.timepicker": "js/vendor/timepicker/jquery.timepicker",
#            "jquery.cookie": "js/vendor/jquery.cookie",
#            "jquery.qtip": "js/vendor/jquery.qtip.min",
#            "jquery.scrollTo": "js/vendor/jquery.scrollTo-1.4.2-min",
#            "jquery.flot": "js/vendor/flot/jquery.flot.min",
#            "jquery.fileupload": "js/vendor/jQuery-File-Upload/js/jquery.fileupload",
#            "jquery.iframe-transport": "js/vendor/jQuery-File-Upload/js/jquery.iframe-transport",
#            "jquery.inputnumber": "js/vendor/html5-input-polyfills/number-polyfill",
#            "jquery.immediateDescendents": "coffee/src/jquery.immediateDescendents",
#            "datepair": "js/vendor/timepicker/datepair",
#            "date": "js/vendor/date",
#            "tzAbbr": "js/vendor/tzAbbr",
#            "underscore": "js/vendor/underscore-min",
#            "underscore.string": "js/vendor/underscore.string.min",
#            "backbone": "js/vendor/backbone-min",
#            "backbone.associations": "js/vendor/backbone-associations-min",
#            "backbone.paginator": "js/vendor/backbone.paginator.min",
#            "tinymce": "js/vendor/tiny_mce/tiny_mce",
#            "jquery.tinymce": "js/vendor/tiny_mce/jquery.tinymce",
#            "xmodule": "/xmodule/xmodule",
#            "xblock": "coffee/src/xblock",
#            "utility": "js/src/utility",
#            "accessibility": "js/src/accessibility_tools",
#            "draggabilly": "js/vendor/draggabilly.pkgd",
#            "URI": "js/vendor/URI.min",
#
#            // externally hosted files
#            "tender": "//edxedge.tenderapp.com/tender_widget",
#
#            "youtube": [
#                // youtube URL does not end in ".js". We add "?noext" to the path so
#                // that require.js adds the ".js" to the query component of the URL,
#                // and leaves the path component intact.
#                "//www.youtube.com/player_api?noext",
#                // if youtube fails to load, fallback on a local file
#                // so that require doesn't fall over
#                "js/src/youtube_fallback"
#            ]
#        },
#        shim: {
#            "gettext": {
#                exports: "gettext"
#            },
#            "date": {
#                exports: "Date"
#            },
#            "jquery.ui": {
#                deps: ["jquery"],
#                exports: "jQuery.ui"
#            },
#            "jquery.form": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.ajaxForm"
#            },
#            "jquery.markitup": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.markitup"
#            },
#            "jquery.leanmodal": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.leanModal"
#            },
#            "jquery.ajaxQueue": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.ajaxQueue"
#            },
#            "jquery.smoothScroll": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.smoothScroll"
#            },
#            "jquery.cookie": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.cookie"
#            },
#            "jquery.qtip": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.qtip"
#            },
#            "jquery.scrollTo": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.scrollTo",
#            },
#            "jquery.flot": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.plot"
#            },
#            "jquery.fileupload": {
#                deps: ["jquery.iframe-transport"],
#                exports: "jQuery.fn.fileupload"
#            },
#            "jquery.inputnumber": {
#                deps: ["jquery"],
#                exports: "jQuery.fn.inputNumber"
#            },
#            "jquery.tinymce": {
#                deps: ["jquery", "tinymce"],
#                exports: "jQuery.fn.tinymce"
#            },
#            "datepair": {
#                deps: ["jquery.ui", "jquery.timepicker"]
#            },
#            "underscore": {
#                exports: "_"
#            },
#            "backbone": {
#                deps: ["underscore", "jquery"],
#                exports: "Backbone"
#            },
#            "backbone.associations": {
#                deps: ["backbone"],
#                exports: "Backbone.Associations"
#            },
#            "backbone.paginator": {
#                deps: ["backbone"],
#                exports: "Backbone.Paginator"
#            },
#            "youtube": {
#                exports: "YT"
#            },
#            "codemirror": {
#                exports: "CodeMirror"
#            },
#            "codemirror/stex": {
#                deps: ["codemirror"]
#            },
#            "tinymce": {
#                exports: "tinymce"
#            },
#            "mathjax": {
#                exports: "MathJax",
#                init: function() {
#                  MathJax.Hub.Config({
#                    tex2jax: {
#                      inlineMath: [
#                        ["\\(","\\)"],
#                        ['[mathjaxinline]','[/mathjaxinline]']
#                      ],
#                      displayMath: [
#                        ["\\[","\\]"],
#                        ['[mathjax]','[/mathjax]']
#                      ]
#                    }
#                  });
#                  MathJax.Hub.Configured();
#                }
#            },
#            "URI": {
#                exports: "URI"
#            },
#            "xblock/core": {
#                exports: "XBlock",
#                deps: ["jquery", "jquery.immediateDescendents"]
#            },
#            "xblock/runtime.v1": {
#                exports: "XBlock",
#                deps: ["xblock/core"]
#            },
#
#            "coffee/src/main": {
#                deps: ["coffee/src/ajax_prefix"]
#            },
#            "coffee/src/logger": {
#                exports: "Logger",
#                deps: ["coffee/src/ajax_prefix"]
#            }
#        },
#        // load jquery and gettext automatically
#        deps: ["jquery", "gettext"],
#        callback: function() {
#            // load other scripts on every page, after jquery loads
#            require(["js/base", "coffee/src/main", "coffee/src/logger", "datepair", "accessibility"]);
#            // we need "datepair" because it dynamically modifies the page
#            // when it is loaded -- yuck!
#        }
#    };
#    </script>
#            <script type="text/javascript" src="js/vendor/require.js"></script>
#
#            <script id="system-feedback-tpl" type="text/template">
#      <div class="wrapper wrapper-&lt;%= type %&gt; wrapper-&lt;%= type %&gt;-&lt;%= intent %&gt;
#            &lt;% if(obj.shown) { %&gt;is-shown&lt;% } else { %&gt;is-hiding&lt;% } %&gt;
#            &lt;% if(_.contains(['help', 'mini'], intent)) { %&gt;wrapper-&lt;%= type %&gt;-status&lt;% } %&gt;" id="&lt;%= type %&gt;-&lt;%= intent %&gt;" aria-hidden="&lt;% if(obj.shown) { %&gt;false&lt;% } else { %&gt;true&lt;% } %&gt;" aria-labelledby="&lt;%= type %&gt;-&lt;%= intent %&gt;-title">
#  <div class="&lt;%= type %&gt; &lt;%= intent %&gt; &lt;% if(obj.actions) { %&gt;has-actions&lt;% } %&gt;">
#    &lt;% if(obj.icon) { %&gt;
#      &lt;% var iconClass = {"warning": "warning-sign", "confirmation": "ok", "error": "warning-sign", "announcement": "bullhorn", "step-required": "exclamation-sign", "help": "question-sign", "mini": "cog"} %&gt;
#      <i class="icon-&lt;%= iconClass[intent] %&gt;"></i>
#    &lt;% } %&gt;
#
#    <div class="copy">
#      <h2 class="title title-3" id="&lt;%= type %&gt;-&lt;%= intent %&gt;-title">&lt;%= title %&gt;</h2>
#      &lt;% if(obj.message) { %&gt;<p class="message" id="&lt;%= type %&gt;-&lt;%= intent %&gt;-description">&lt;%= message %&gt;</p>&lt;% } %&gt;
#    </div>
#
#    &lt;% if(obj.actions) { %&gt;
#    <nav class="nav-actions">
#      <h3 class="sr">&lt;%= type %&gt; Actions</h3>
#      <ul>
#        &lt;% if(actions.primary) { %&gt;
#        <li class="nav-item">
#          <a href="#" class="button action-primary &lt;%= actions.primary.class %&gt;">&lt;%= actions.primary.text %&gt;</a>
#        </li>
#        &lt;% } %&gt;
#        &lt;% if(actions.secondary) {
#             _.each(actions.secondary, function(secondary) { %&gt;
#        <li class="nav-item">
#          <a href="#" class="button action-secondary &lt;%= secondary.class %&gt;">&lt;%= secondary.text %&gt;</a>
#        </li>
#        &lt;%   });
#           } %&gt;
#      </ul>
#    </nav>
#    &lt;% } %&gt;
#
#    &lt;% if(obj.closeIcon) { %&gt;
#    <a href="#" rel="view" class="action action-close action-&lt;%= type %&gt;-close">
#      <i class="icon-remove-sign"></i>
#      <span class="label">close &lt;%= type %&gt;</span>
#    </a>
#    &lt;% } %&gt;
#  </div>
#</div>
#
#    </script>
#
#
#            <script type="text/javascript">
#  require(['js/models/course'], function(Course) {
#    window.course = new Course({
#      id: "MITx/999/Robot_Super_Course",
#      name: "Robot Super Course",
#      url_name: "Robot_Super_Course",
#      org: "MITx",
#      num: "999",
#      revision: "None"
#    });
#  });
#      </script>
#
#            <!-- view -->
#            <div class="wrapper wrapper-view">
#                <div class="wrapper-header wrapper" id="view-top">
#                    <header class="primary" role="banner"> <div class="wrapper wrapper-l">
#                            <h1 class="branding"><a href="/"><img src="img/logo-edx-studio.png"
#                                        alt="edX Studio" /></a></h1>
#                            <h2 class="info-course">
#                                <span class="sr">Current Course:</span>
#                                <a class="course-link"
#                                    href="/course/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course">
#                                    <span class="course-org">MITx</span><span class="course-number"
#                                        >999</span>
#                                    <span class="course-title" title="Robot Super Course">Robot
#                                        Super Course</span>
#                                </a>
#                            </h2>
#                            <nav class="nav-course nav-dd ui-left">
#                                <h2 class="sr">Robot Super Course's Navigation:</h2>
#                                <ol>
#                                    <li class="nav-item nav-course-courseware">
#                                        <h3 class="title"><span class="label"><span
#                                                  class="label-prefix sr">Course
#                                                </span>Content</span>
#                                            <i class="icon-caret-down ui-toggle-dd"></i></h3>
#                                        <div class="wrapper wrapper-nav-sub">
#                                            <div class="nav-sub">
#                                                <ul>
#                                                  <li class="nav-item nav-course-courseware-outline">
#                                                  <a
#                                                  href="/course/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Outline</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-courseware-updates">
#                                                  <a
#                                                  href="/course_info/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Updates</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-courseware-pages">
#                                                  <a
#                                                  href="/tabs/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Static Pages</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-courseware-uploads">
#                                                  <a
#                                                  href="/assets/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Files &amp; Uploads</a>
#                                                  </li>
#                                                  <li
#                                                  class="nav-item nav-course-courseware-textbooks">
#                                                  <a
#                                                  href="/textbooks/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Textbooks</a>
#                                                  </li>
#                                                </ul>
#                                            </div>
#                                        </div>
#                                    </li>
#
#                                    <li class="nav-item nav-course-settings">
#                                        <h3 class="title"><span class="label"><span
#                                                  class="label-prefix sr">Course
#                                                </span>Settings</span>
#                                            <i class="icon-caret-down ui-toggle-dd"></i></h3>
#                                        <div class="wrapper wrapper-nav-sub">
#                                            <div class="nav-sub">
#                                                <ul>
#                                                  <li class="nav-item nav-course-settings-schedule">
#                                                  <a
#                                                  href="/settings/details/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Schedule &amp; Details</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-settings-grading">
#                                                  <a
#                                                  href="/settings/grading/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Grading</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-settings-team">
#                                                  <a
#                                                  href="/course_team/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Course Team</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-settings-advanced">
#                                                  <a
#                                                  href="/settings/advanced/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Advanced Settings</a>
#                                                  </li>
#                                                </ul>
#                                            </div>
#                                        </div>
#                                    </li>
#
#                                    <li class="nav-item nav-course-tools">
#                                        <h3 class="title"><span class="label">Tools</span>
#                                            <i class="icon-caret-down ui-toggle-dd"></i></h3>
#                                        <div class="wrapper wrapper-nav-sub">
#                                            <div class="nav-sub">
#                                                <ul>
#                                                  <li class="nav-item nav-course-tools-checklists">
#                                                  <a
#                                                  href="/checklists/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Checklists</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-tools-import">
#                                                  <a
#                                                  href="/import/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Import</a>
#                                                  </li>
#                                                  <li class="nav-item nav-course-tools-export">
#                                                  <a
#                                                  href="/export/MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                                  >Export</a>
#                                                  </li>
#                                                </ul>
#                                            </div>
#                                        </div>
#                                    </li>
#                                </ol>
#                            </nav>
#                        </div> <div class="wrapper wrapper-r">
#                            <nav class="nav-account nav-is-signedin nav-dd ui-right">
#                                <h2 class="sr">Help &amp; Account Navigation</h2> <ol>
#                                    <li class="nav-item nav-account-help">
#                                        <h3 class="title"><span class="label">Help</span>
#                                            <i class="icon-caret-down ui-toggle-dd"></i></h3>
#                                        <div class="wrapper wrapper-nav-sub">
#                                            <div class="nav-sub">
#                                                <ul>
#                                                  <li class="nav-item nav-help-documentation">
#                                                  <a
#                                                  href="http://files.edx.org/Getting_Started_with_Studio.pdf"
#                                                  title="This is a PDF Document">Studio
#                                                  Documentation</a>
#                                                  </li>
#                                                  <li class="nav-item nav-help-helpcenter">
#                                                  <a href="http://help.edge.edx.org/" rel="external"
#                                                  >Studio Help Center</a>
#                                                  </li>
#                                                  <li class="nav-item nav-help-feedback">
#                                                  <a href="http://help.edge.edx.org/discussion/new"
#                                                  class="show-tender"
#                                                  title="Use our feedback tool, Tender, to share your feedback"
#                                                  >Contact Us</a>
#                                                  </li>
#                                                </ul>
#                                            </div>
#                                        </div>
#                                    </li>
#
#                                    <li class="nav-item nav-account-user">
#                                        <h3 class="title"><span class="label"><span
#                                                  class="label-prefix sr">Currently signed in
#                                                  as:</span><span class="account-username"
#                                                  title="testuser">testuser</span></span>
#                                            <i class="icon-caret-down ui-toggle-dd"></i></h3>
#                                        <div class="wrapper wrapper-nav-sub">
#                                            <div class="nav-sub">
#                                                <ul>
#                                                  <li class="nav-item nav-account-dashboard">
#                                                  <a href="/">My Courses</a>
#                                                  </li>
#                                                  <li class="nav-item nav-account-signout">
#                                                  <a class="action action-signout" href="/logout"
#                                                  >Sign Out</a>
#                                                  </li>
#                                                </ul>
#                                            </div>
#                                        </div>
#                                    </li>
#                                </ol>
#                            </nav>
#                        </div>
#                    </header>
#                </div>
#                <div id="page-alert"></div>
#                <div id="content">
#                    <div class="wrapper-mast wrapper">
#                        <header class="mast has-actions has-subtitle">
#                            <h1 class="page-header">
#                                <small class="subtitle">Content</small>
#                                <span class="sr">&gt; </span>Course Outline </h1> <nav
#                                class="nav-actions">
#                                <h3 class="sr">Page Actions</h3>
#                                <ul>
#                                    <li class="nav-item">
#                                        <a href="#" class="toggle-button toggle-button-sections"><i
#                                                class="icon-arrow-up"></i>
#                                            <span class="label">Collapse All Sections</span></a>
#                                    </li>
#                                    <li class="nav-item">
#                                        <a href="#"
#                                            class="button new-button new-courseware-section-button"
#                                                ><i class="icon-plus"></i> New Section</a>
#                                    </li>
#                                    <li class="nav-item">
#                                        <a
#                                            href="//localhost:8000/courses/MITx/999/Robot_Super_Course/jump_to/i4x://MITx/999/course/Robot_Super_Course"
#                                            rel="external"
#                                            class="button view-button view-live-button">View
#                                            Live</a>
#                                    </li>
#                                </ul>
#                            </nav>
#                        </header>
#                    </div>
#                    <div class="wrapper-content wrapper">
#                        <section class="content">
#                            <article class="content-primary" role="main"> <div class="wrapper-dnd">
#                                    <article class="courseware-overview"
#                                        data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                        > <section
#                                            class="courseware-section is-collapsible is-draggable"
#                                            data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                            data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Dog">
#                                            <span
#                                                class="draggable-drop-indicator draggable-drop-indicator-before"
#                                                  ><i class="icon-caret-right"></i></span> <header
#                                                class="section">
#                                                <a href="#"
#                                                  data-tooltip="Expand/collapse this section"
#                                                  class="action expand-collapse collapse">
#                                                  <i class="icon-caret-down ui-toggle-expansion"></i>
#                                                  <span class="sr">Expand/collapse this
#                                                  section</span>
#                                                </a> <div class="item-details"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Dog">
#                                                  <h3 class="section-name" data-name="Dog"></h3>
#                                                </div>
#                                                <div class="item-actions">
#                                                  <ul class="actions-list">
#
#
#
#                                                  <li class="actions-item pubdate">
#                                                  <div class="section-published-date">
#                                                  <span class="published-status"><strong>Release
#                                                  date:</strong> Jan 01, 2030 at 00:00 UTC</span>
#                                                  <a href="#" class="edit-release-date action"
#                                                  data-date="01/01/2030" data-time="00:00"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Dog"
#                                                  ><i class="icon-time"></i>
#                                                  <span class="sr">Edit section release
#                                                  date</span></a>
#                                                  </div>
#                                                  </li>
#                                                  <li class="actions-item delete">
#                                                  <a href="#" data-tooltip="Delete this section"
#                                                  class="action delete-section-button"><i
#                                                  class="icon-trash"></i>
#                                                  <span class="sr">Delete section</span></a>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <span data-tooltip="Drag to reorder"
#                                                  class="drag-handle section-drag-handle action"
#                                                  ><span class="sr"> Drag to reorder
#                                                  section</span></span>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <i
#                                                  class="icon-circle       unit-status-all-public unit-status-change-section">
#                                                  <!-- div elements are invisible containers to hold unit counts and a list of locations -->
#                                                  <div hidden="true" class="public_count"> 1 </div>
#                                                  <div hidden="true" class="private_count"> 0 </div>
#                                                  <div hidden="true" class="draft_count"> 0 </div>
#                                                  <div hidden="true" class="unit_locator_list">
#                                                  MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a;
#                                                  </div>
#                                                  </i>
#                                                  </li>
#                                                  </ul>
#                                                </div>
#                                            </header>
#                                            <div class="subsection-list">
#                                                <ol class="sortable-subsection-list">
#
#
#
#
#
#
#
#                                                  <li
#                                                  class="courseware-subsection collapsed id-holder is-draggable is-collapsible "
#                                                  data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Dog"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend">
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-before"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  <div class="section-item">
#                                                  <div class="details">
#                                                  <canvas
#                                                  id="canvas_MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend"
#                                                  width="5" height="12"
#                                                  style="border:1px solid #000000;"> </canvas>
#                                                  <script>
#        var c=document.getElementById("canvas_MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend");
#        var ctx=c.getContext("2d");
#        ctx.fillStyle="#FF0000 ";
#        ctx.fillRect(0,0,20,20);
#    </script>
#                                                  <a href="#"
#                                                  data-tooltip="Expand/collapse this subsection"
#                                                  class="action expand-collapse expand">
#                                                  <i class="icon-caret-down ui-toggle-expansion"></i>
#                                                  <span class="sr">Expand/collapse this
#                                                  subsection</span>
#                                                  </a>
#                                                  <a
#                                                  href="/subsection/MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend"
#                                                  style="width:400">
#                                                  <span class="subsection-name">
#                                                  <span class="subsection-name-value"> Best Friend
#                                                  </span>
#                                                  </span>
#                                                  </a>
#                                                  </div>
#                                                  <div class="item-actions">
#                                                  <ul class="actions-list">
#                                                  <li class="actions-item grades">
#                                                  <div class="gradable-status"
#                                                  data-initial-status="Not Graded"></div>
#                                                  </li>
#                                                  <li class="actions-item delete">
#                                                  <a href="#" data-tooltip="Delete this subsection"
#                                                  class="action delete-subsection-button"><i
#                                                  class="icon-trash"></i>
#                                                  <span class="sr">Delete subsection</span></a>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <span data-tooltip="Drag to reorder"
#                                                  class="drag-handle subsection-drag-handle action"
#                                                  ></span>
#                                                  </li>
#
#                                                  <li class="actions-item">
#                                                  <i
#                                                  class="icon-circle       unit-status-all-public unit-status-change-subsection">
#                                                  <!-- div elements are invisible containers to hold unit counts and a list of locations -->
#                                                  <div hidden="true" class="public_count"> 1 </div>
#                                                  <div hidden="true" class="private_count"> 0 </div>
#                                                  <div hidden="true" class="draft_count"> 0 </div>
#                                                  <div hidden="true" class="unit_locator_list">
#                                                  MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a;
#                                                  </div>
#                                                  </i>
#                                                  </li>
#                                                  </ul>
#                                                  </div>
#                                                  </div>
#                                                  <ol class="sortable-unit-list">
#
#
#
#                                                  <li class="courseware-unit unit is-draggable"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a"
#                                                  data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend">
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-before"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  <div class="section-item ">
#                                                  <a
#                                                  href="/unit/MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a"
#                                                  class="public-item">
#                                                  <span class="unit-name">Unit 1a</span>
#                                                  </a>
#                                                  <div class="item-actions">
#                                                  <ul class="actions-list">
#                                                  <li class="actions-item delete">
#                                                  <a href="#" data-tooltip="Delete this unit"
#                                                  class="delete-unit-button action"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a"
#                                                  ><i class="icon-trash"></i><span class="sr">Delete
#                                                  unit</span></a>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <span data-tooltip="Drag to sort"
#                                                  class="drag-handle unit-drag-handle action"><span
#                                                  class="sr"> Drag to reorder unit</span></span>
#                                                  </li>
#
#                                                  <a href="#" data-tooltip="Change unit status">
#                                                  <i
#                                                  class="icon-circle       unit-status-all-public unit-status-change-unit">
#                                                  <!-- div elements are invisible containers to hold unit counts and a list of locations -->
#                                                  <div hidden="true" class="public_count"> 1 </div>
#                                                  <div hidden="true" class="private_count"> 0 </div>
#                                                  <div hidden="true" class="draft_count"> 0 </div>
#                                                  <div hidden="true" class="unit_locator_list">
#                                                  MITx.999.Robot_Super_Course/branch/draft/block/Unit_1a
#                                                  </div>
#                                                  </i>
#                                                  </a>
#                                                  </ul>
#                                                  </div>
#                                                  </div>
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-after"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  </li>
#                                                  <li class="courseware-unit add-new-unit">
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-initial"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  <a href="#" class="new-unit-item"
#                                                  data-category="vertical"
#                                                  data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Best_Friend">
#                                                  <i class="icon-plus"></i> New Unit </a>
#                                                  </li>
#                                                  </ol>
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-after"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  </li>
#                                                  <li class="ui-splint ui-splint-indicator">
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-initial"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  </li>
#                                                </ol>
#                                                <div class="list-header new-subsection">
#                                                  <a href="#" class="new-subsection-item"
#                                                  data-category="sequential">
#                                                  <i class="icon-plus"></i> New Subsection </a>
#                                                </div>
#                                            </div> <span
#                                                class="draggable-drop-indicator draggable-drop-indicator-after"
#                                                  ><i class="icon-caret-right"></i></span>
#                                        </section> <section
#                                            class="courseware-section is-collapsible is-draggable"
#                                            data-parent="MITx.999.Robot_Super_Course/branch/draft/block/Robot_Super_Course"
#                                            data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Cat">
#                                            <span
#                                                class="draggable-drop-indicator draggable-drop-indicator-before"
#                                                  ><i class="icon-caret-right"></i></span> <header
#                                                class="section">
#                                                <a href="#"
#                                                  data-tooltip="Expand/collapse this section"
#                                                  class="action expand-collapse collapse">
#                                                  <i class="icon-caret-down ui-toggle-expansion"></i>
#                                                  <span class="sr">Expand/collapse this
#                                                  section</span>
#                                                </a> <div class="item-details"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Cat">
#                                                  <h3 class="section-name" data-name="Cat"></h3>
#                                                </div>
#                                                <div class="item-actions">
#                                                  <ul class="actions-list">
#
#
#
#                                                  <li class="actions-item pubdate">
#                                                  <div class="section-published-date">
#                                                  <span class="published-status"><strong>Release
#                                                  date:</strong> Jan 01, 2030 at 00:00 UTC</span>
#                                                  <a href="#" class="edit-release-date action"
#                                                  data-date="01/01/2030" data-time="00:00"
#                                                  data-locator="MITx.999.Robot_Super_Course/branch/draft/block/Cat"
#                                                  ><i class="icon-time"></i>
#                                                  <span class="sr">Edit section release
#                                                  date</span></a>
#                                                  </div>
#                                                  </li>
#                                                  <li class="actions-item delete">
#                                                  <a href="#" data-tooltip="Delete this section"
#                                                  class="action delete-section-button"><i
#                                                  class="icon-trash"></i>
#                                                  <span class="sr">Delete section</span></a>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <span data-tooltip="Drag to reorder"
#                                                  class="drag-handle section-drag-handle action"
#                                                  ><span class="sr"> Drag to reorder
#                                                  section</span></span>
#                                                  </li>
#                                                  <li class="actions-item drag">
#                                                  <i class=" unit-status-change-section">
#                                                  <!-- div elements are invisible containers to hold unit counts and a list of locations -->
#                                                  <div hidden="true" class="public_count"> 0 </div>
#                                                  <div hidden="true" class="private_count"> 0 </div>
#                                                  <div hidden="true" class="draft_count"> 0 </div>
#                                                  <div hidden="true" class="unit_locator_list"
#                                                  > </div>
#                                                  </i>
#                                                  </li>
#                                                  </ul>
#                                                </div>
#                                            </header>
#                                            <div class="subsection-list">
#                                                <ol class="sortable-subsection-list">
#                                                  <li class="ui-splint ui-splint-indicator">
#                                                  <span
#                                                  class="draggable-drop-indicator draggable-drop-indicator-initial"
#                                                  ><i class="icon-caret-right"></i></span>
#                                                  </li>
#                                                </ol>
#                                                <div class="list-header new-subsection">
#                                                  <a href="#" class="new-subsection-item"
#                                                  data-category="sequential">
#                                                  <i class="icon-plus"></i> New Subsection </a>
#                                                </div>
#                                            </div> <span
#                                                class="draggable-drop-indicator draggable-drop-indicator-after"
#                                                  ><i class="icon-caret-right"></i></span>
#                                        </section>
#                                    </article>
#                                </div> </article>
#                            <aside class="content-supplementary" role="complimentary">
#                                <div class="bit">
#                                    <h3 class="title-3">What can I do on this page?</h3>
#                                    <p>You can create new sections and subsections, set the release
#                                        date for sections, and create new units in existing
#                                        subsections. You can set the assignment type for subsections
#                                        that are to be graded, and you can open a subsection for
#                                        further editing.</p>
#                                    <p>In addition, you can drag and drop sections, subsections, and
#                                        units to reorganize your course.</p>
#                                </div>
#                            </aside>
#                        </section>
#                    </div>
#                    <footer></footer>
#                    <div
#                        class="wrapper wrapper-dialog wrapper-dialog-edit-sectionrelease edit-section-publish-settings"
#                        aria-describedby="dialog-edit-sectionrelease-description"
#                        aria-labelledby="dialog-edit-sectionrelease-title" aria-hidden=""
#                        role="dialog">
#                        <div class="dialog confirm">
#                            <form class="edit-sectionrelease-dialog" action="#">
#                                <div class="form-content">
#                                    <h2 class="title dialog-edit-sectionrelease-title">Section
#                                        Release Date</h2>
#                                    <p id="dialog-edit-sectionrelease-description" class="message"
#                                        >On the date set below, this section - <strong
#                                            class="section-name"></strong> - will be released to
#                                        students. Any units marked private will only be visible to
#                                        admins.</p>
#                                    <ul class="list-input picker datepair">
#                                        <li class="field field-start-date">
#                                            <label for="start_date">Release Day</label>
#                                            <input class="start-date date" type="text"
#                                                name="start_date" value="" placeholder="MM/DD/YYYY"
#                                                size="15" autocomplete="off" />
#                                        </li>
#                                        <li class="field field-start-time">
#                                            <label for="start_time">Release Time (<abbr
#                                                  title="Coordinated Universal Time"
#                                                >UTC</abbr>)</label>
#                                            <input class="start-time time" type="text"
#                                                name="start_time" value="" placeholder="HH:MM"
#                                                size="10" autocomplete="off" />
#                                        </li>
#                                    </ul>
#                                </div>
#                                <div class="actions">
#                                    <h3 class="sr">Form Actions</h3>
#                                    <ul>
#                                        <li class="action-item">
#                                            <a href="#" class="button action-primary action-save"
#                                                >Save</a>
#                                        </li>
#                                        <li class="action-item">
#                                            <a href="#"
#                                                class="button action-secondary action-cancel"
#                                                >Cancel</a>
#                                        </li>
#                                    </ul>
#                                </div>
#                            </form>
#                        </div>
#                    </div>
#                </div>
#                <script type="text/javascript">
#        require(['js/sock']);
#      </script>
#                <div class="wrapper-sock wrapper">
#                    <ul class="list-actions list-cta">
#                        <li class="action-item">
#                            <a href="#sock" class="cta cta-show-sock"><i class="icon-question-sign"></i>
#                                <span class="copy">Looking for Help with Studio?</span></a>
#                        </li>
#                    </ul>
#                    <div class="wrapper-inner wrapper">
#                        <section class="sock" id="sock">
#                            <header>
#                                <h2 class="title sr">edX Studio Help</h2>
#                            </header> <div class="support">
#                                <h3 class="title">Studio Support</h3>
#                                <div class="copy">
#                                    <p>Need help with Studio? Creating a course is complex, so we're
#                                        here to help. Take advantage of our documentation, help
#                                        center, as well as our edX101 introduction course for course
#                                        authors.</p>
#                                </div>
#                                <ul class="list-actions">
#                                    <li class="action-item">
#                                        <a
#                                            href="http://files.edx.org/Getting_Started_with_Studio.pdf"
#                                            class="action action-primary"
#                                            title="This is a PDF Document">Download Studio
#                                            Documentation</a>
#                                        <span class="tip">How to use Studio to build your
#                                            course</span>
#                                    </li>
#                                    <li class="action-item">
#                                        <a href="http://help.edge.edx.org/" rel="external"
#                                            class="action action-primary">Studio Help Center</a>
#                                        <span class="tip">Studio Help Center</span>
#                                    </li>
#                                    <li class="action-item">
#                                        <a
#                                            href="https://edge.edx.org/courses/edX/edX101/How_to_Create_an_edX_Course/about"
#                                            rel="external" class="action action-primary">Enroll in
#                                            edX101</a>
#                                        <span class="tip">How to use Studio to build your
#                                            course</span>
#                                    </li>
#                                </ul>
#                            </div> <div class="feedback">
#                                <h3 class="title">Contact us about Studio</h3>
#                                <div class="copy">
#                                    <p>Have problems, questions, or suggestions about Studio? We're
#                                        also here to listen to any feedback you want to share.</p>
#                                </div>
#                                <ul class="list-actions">
#                                    <li class="action-item">
#                                        <a href="http://help.edge.edx.org/discussion/new"
#                                            class="action action-primary show-tender"
#                                            title="Use our feedback tool, Tender, to share your feedback"
#                                                ><i class="icon-comments"></i>Contact Us</a>
#                                    </li>
#                                </ul>
#                            </div>
#                        </section>
#                    </div>
#                </div>
#                <div class="wrapper-footer wrapper">
#                    <footer class="primary" role="contentinfo">
#                        <div class="colophon">
#                            <p><a href="http://www.edx.org" rel="external">edX</a>. All rights
#                                reserved.</p>
#                        </div> <nav class="nav-peripheral">
#                            <ol>
#                                <li class="nav-item nav-peripheral-tos">
#                                    <a data-rel="edx.org" href="#">Terms of Service</a>
#                                </li>
#                                <li class="nav-item nav-peripheral-pp">
#                                    <a data-rel="edx.org" href="#">Privacy Policy</a>
#                                </li>
#                                <li class="nav-item nav-peripheral-feedback">
#                                    <a href="http://help.edge.edx.org/discussion/new"
#                                        class="show-tender"
#                                        title="Use our feedback tool, Tender, to share your feedback"
#                                        >Contact Us</a>
#                                </li>
#                            </ol>
#                        </nav>
#                    </footer>
#                </div>
#                <script type="text/javascript">
#window.Tender = {
#  hideToggle: true,
#  title: '',
#  body: '',
#  hide_kb: 'true',
#  widgetToggles: document.getElementsByClassName('show-tender')
#}
#require(['tender']);
#</script>
#                <div id="page-notification"></div>
#            </div>
#
#            <div id="page-prompt"></div>
#
#            <link rel="stylesheet" type="text/css" href="js/vendor/timepicker/jquery.timepicker.css" />
#            <link rel="stylesheet" type="text/css"
#                href="css/vendor/html5-input-polyfills/number-polyfill.css" />
#            <script type="text/template" id="section-name-edit-tpl">
#    <form class="section-name-edit">
#    <input type="text" value="&lt;%= name %&gt;" autocomplete="off" />
#    <input type="submit" class="save-button" value="&lt;%= gettext('Save') %&gt;" />
#    <input type="button" class="cancel-button" value="&lt;%= gettext('Cancel') %&gt;" />
#</form>
#
#  </script>
#
#            <script type="text/javascript">
#require(["domReady!", "jquery", "js/models/location", "js/models/section", "js/views/section_show", "js/views/overview_assignment_grader", "js/collections/course_grader", "js/views/overview", "jquery.inputnumber"],
#    function(doc, $, Location, SectionModel, SectionShowView, OverviewAssignmentGrader, CourseGraderCollection){
#  // TODO figure out whether these should be in window or someplace else or whether they're only needed as local vars
#  // I believe that current (New Section/New Subsection) cause full page reloads which means these aren't needed globally
#  // but we really should change that behavior.
#  if (!window.graderTypes) {
#    window.graderTypes = new CourseGraderCollection([{"weight": 15.0, "short_label": "HW", "id": 0, "min_count": 12, "type": "Homework", "drop_count": 2}, {"weight": 15.0, "short_label": "", "id": 1, "min_count": 12, "type": "Lab", "drop_count": 2}, {"weight": 30.0, "short_label": "Midterm", "id": 2, "min_count": 1, "type": "Midterm Exam", "drop_count": 0}, {"weight": 40.0, "short_label": "Final", "id": 3, "min_count": 1, "type": "Final Exam", "drop_count": 0}], {parse:true});
#  }
#
#  $(".gradable-status").each(function(index, ele) {
#      var gradeView = new OverviewAssignmentGrader({
#          el : ele,
#          graders : window.graderTypes
#      });
#  });
#
#  $(".section-name").each(function() {
#      var model = new SectionModel({
#          id: $(this).parent(".item-details").data("locator"),
#          name: $(this).data("name")
#      });
#      new SectionShowView({model: model, el: this}).render();
#  })
#});
#  </script>
#
#            <div class="modal-cover"></div>
#        </body>
#
#    </html>
#    '''
#
