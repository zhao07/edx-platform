# -*- coding: utf-8 -*-

"""
Acceptance tests for Video.
"""

from unittest import skip

from .helpers import UniqueCourseTest, load_data_str
from ..pages.lms.video import VideoPage
from ..pages.lms.tab_nav import TabNavPage
from ..pages.lms.course_nav import CourseNavPage
from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.lms.course_info import CourseInfoPage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc


HTML5_SOURCES = [
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.mp4',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.webm',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.ogv',
]

HTML5_SOURCES_INCORRECT = [
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.mp99',
]


class VideoTestA(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestA, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video')
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_rendered_in_youtube_without_html5_sources(self):
        """
        Tests that Video component is rendered in Youtube mode without HTML5 sources Given the course
        has a Video component in "Youtube" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # check if video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))


class VideoTestB(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestB, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_not_rendered_in_youtube_with_html5_sources(self):
        """
        Tests that Video component is not rendered in Youtube mode with HTML5 sources Given the course
        has a Video component in "Youtube_HTML5" mode.
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # check if video has rendered in "html5" mode
        self.assertTrue(self.video.is_video_rendered('html5'))


class VideoTestC(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestC, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_fully_rendered_in_html5_mode(self):
        """
        Tests that Video component is fully rendered in HTML5 mode Given the course has a Video component
        in "HTML5" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "HTML5" mode
        self.assertTrue(self.video.is_video_rendered('html5'))

        # check if all sources are correct. It means page has video source urls that match exactly with `HTML5_SOURCES`
        self.assertEqual(self.video.get_all_video_sources, HTML5_SOURCES)

    def test_autoplay_disabled_for_video_component(self):
        """
        Tests that Autoplay is disabled in for a Video component Given the course has a Video component in HTML5 mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # check if the video has autoplay mode disabled
        self.assertFalse(self.video.is_autoplay_enabled)


class VideoTestD(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestD, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES_INCORRECT
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_rendered_in_html5_with_unsupported_html5_sources(self):
        """
        Tests that Video component is rendered in HTML5 mode with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "HTML5_Unsupported_Video" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # check if error message is shown
        self.assertTrue(self.video.is_error_message_shown)

        # check if error message has correct text
        correct_error_message_text = 'ERROR: No playable video sources found!'
        self.assertIn(correct_error_message_text, self.video.get_error_message_text)


class VideoTestE(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestE, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        html5_metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'A')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-1').add_children(
                        XBlockFixtureDesc('video', 'B')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-2').add_children(
                        XBlockFixtureDesc('video', 'C', metadata=html5_metadata)
        )

                ))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()


class VideoTestH(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestH, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'transcripts': {'zh': 'chinese_transcripts.srt'}
        }

        course_fix.add_asset('chinese_transcripts.srt')

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_cc_button_works_correctly_without_english_transcript_youtube_mode(self):
        """
        Tests that CC button works correctly w/o english transcript in Youtube mode of Video component
        Given I have a "chinese_transcripts.srt" transcript file in assets And it has a video in "Youtube" mode.
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)


class VideoTestQ(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestQ, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        b_metadata = {
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'A'),
                        XBlockFixtureDesc('video', 'B', metadata=b_metadata),
                        XBlockFixtureDesc('video', 'C'),
                        XBlockFixtureDesc('video', 'D')

        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-1').add_children(
                        XBlockFixtureDesc('video', 'E'),
                        XBlockFixtureDesc('video', 'F'),
                        XBlockFixtureDesc('video', 'G')
        )

                ))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_multiple_videos_in_sequentials_load_and_work(self):
        """
        Tests that Multiple videos in sequentials all load and work, switching between sequentials
        Given
            And it has a video "A" in "Youtube" mode in position "1" of sequential
            And a video "B" in "HTML5" mode in position "1" of sequential
            And a video "C" in "Youtube" mode in position "1" of sequential
            And a video "D" in "Youtube" mode in position "1" of sequential
            And a video "E" in "Youtube" mode in position "2" of sequential
            And a video "F" in "Youtube" mode in position "2" of sequential
            And a video "G" in "Youtube" mode in position "2" of sequential
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # check if video "A" should start playing at speed "1.0"
        self.assertEqual(self.video.get_video_speed, '1.0x')

        # select the "2.0" speed on video "B"
        self.course_nav.go_to_sequential('B')
        self.video.change_speed('2.0')

        # select the "2.0" speed on video "C"
        self.course_nav.go_to_sequential('C')
        self.video.change_speed('2.0')

        # select the "2.0" speed on video "D"
        self.course_nav.go_to_sequential('D')
        self.video.change_speed('2.0')

        # open video "E"
        self.course_nav.go_to_sequential('E')

        # check if video "E" should start playing at speed "2.0"
        self.assertEqual(self.video.get_video_speed, '2.0x')

        # select the "1.0" speed on video "F"
        self.course_nav.go_to_sequential('F')
        self.video.change_speed('1.0')

        # select the "1.0" speed on video "G"
        self.course_nav.go_to_sequential('G')
        self.video.change_speed('1.0')

        # open video "A"
        self.course_nav.go_to_sequential('A')

        # check if video "A" should start playing at speed "2.0"
        self.video.change_speed('2.0')


class VideoTestR(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestR, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        course_fix.add_asset('subs_OEoXaMPEzfM.srt.sjson')

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video')
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_cc_button_works_correctly_transcripts_and_sub_fields_empty(self):
        """
        Tests that CC button works correctly if transcripts and sub fields are empty, but transcript file exists in
        assets (Youtube mode of Video component)
        Given I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets And it has a video in "Youtube" mode
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        self.video.wait_for_video_player()

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if we see "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)