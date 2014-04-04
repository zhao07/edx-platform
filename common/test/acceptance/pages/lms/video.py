"""
Video player in the courseware.
"""

import sys
import time
import requests
from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise, Promise
from bok_choy.javascript import wait_for_js, js_defined


VIDEO_BUTTONS = {
    'CC': '.hide-subtitles',
    'volume': '.volume',
    'play': '.video_control.play',
    'pause': '.video_control.pause',
    'fullscreen': '.add-fullscreen',
    'download_transcript': '.video-tracks > a',
}

VIDEO_MENUS = {
    'language': '.lang .menu',
    'speed': '.speed .menu',
    'download_transcript': '.video-tracks .a11y-menu-list',
}


@js_defined('window.Video')
class VideoPage(PageObject):
    """
    Video player in the courseware.
    """

    url = None

    def is_browser_on_page(self):
        return self.q(css='div.xmodule_VideoModule').present

    @property
    def elapsed_time(self):
        """
        Amount of time elapsed since the start of the video, in seconds.
        """
        elapsed, _ = self._video_time()
        return elapsed

    @property
    def duration(self):
        """
        Total duration of the video, in seconds.
        """
        _, duration = self._video_time()
        return duration

    @property
    def is_playing(self):
        """
        Return a boolean indicating whether the video is playing.
        """
        return self.q(css='a.video_control').present and self.q(css='a.video_control.pause').present

    @property
    def is_paused(self):
        """
        Return a boolean indicating whether the video is paused.
        """
        return self.q(css='a.video_control').present and self.q(css='a.video_control.play').present

    @wait_for_js
    def play(self):
        """
        Start playing the video.
        """
        self.q(css='a.video_control.play').first.click()
        EmptyPromise(lambda: self.is_playing, "Video is playing")

    @wait_for_js
    def pause(self):
        """
        Pause the video.
        """
        self.q(css='a.video_control.pause').first.click()
        EmptyPromise(lambda: self.is_paused, "Video is paused")

    def _video_time(self):
        """
        Return a tuple `(elapsed_time, duration)`, each in seconds.
        """
        # The full time has the form "0:32 / 3:14"
        all_times = self.q(css='div.vidtime').text

        if len(all_times) == 0:
            self.warning('Could not find video time')

        else:
            full_time = all_times[0]

            # Split the time at the " / ", to get ["0:32", "3:14"]
            elapsed_str, duration_str = full_time.split(' / ')

            # Convert each string to seconds
            return self._parse_time_str(elapsed_str), self._parse_time_str(duration_str)

    def _parse_time_str(self, time_str):
        """
        Parse a string of the form 1:23 into seconds (int).
        """
        time_obj = time.strptime(time_str, '%M:%S')
        return time_obj.tm_min * 60 + time_obj.tm_sec

    def is_video_rendered(self, mode):
        """
        Check that if video is rendered in `mode`.
        :param mode: Video mode, `html5` or `youtube`
        """
        modes = {
            'html5': 'video',
            'youtube': 'iframe'
        }

        html_tag = modes[mode]
        EmptyPromise(lambda: self.q(css='.video {0}'.format(html_tag)).present,
                     'Video Rendering Failed in {0} mode.'.format(mode)).fulfill()

        return self.q(css='.speed_link').present

    @property
    def get_all_video_sources(self):
        """
        Extract all video source urls on current page.
        """
        return self.q(css='.video-player video source').map(lambda el: el.get_attribute('src').split('?')[0]).results

    @property
    def is_autoplay_enabled(self):
        """
        Extract `data-autoplay` attribute to check video autoplay is enabled or disabled.
        """
        auto_play = self.q(css='.video').attrs('data-autoplay')[0]

        if auto_play.lower() == 'false':
            return False

        return True

    def click_player_button(self, button):
        """
        Click on `button`.
        :param button: key in VIDEO_BUTTONS dictionary, its value will give us the css selector for `button`
        """
        self.q(css=VIDEO_BUTTONS[button]).first.click()

    def seek_video(self, seek_seconds):
        """
        Seek the video to position specified by `seek_value`.
        :param seek_seconds: Integer value in seconds
        """
        seek_time = float(seek_seconds.strip())
        js_code = "$('.video').data('video-player-state').videoPlayer.onSlideSeek({{time: {0:f}}})".format(seek_time)
        self.browser.execute_script(js_code)

    @property
    def get_video_position(self):
        """
        Extract the current seek position from where Video will start playing
        :return: seek position in format min:sec
        """
        current_seek_position = self.q(css='.vidtime').text
        return current_seek_position.split('/')[0].strip()

    @property
    def is_error_message_shown(self):
        """
        Checks if video player error message shown.
        :return: bool
        """
        return self.q(css='.video .video-player h3').visible

    @property
    def get_error_message_text(self):
        """
        Extract video player error message text.
        :return: str
        """
        return self.q(css='.video .video-player h3').text[0]

    def change_speed(self, speed):
        """
        Change the video play speed.
        :param speed: speed value in str
        """
        self.browser.execute_script("$('.speeds').addClass('open')")
        speed_css = 'li[data-speed="{0}"] a'.format(speed)
        self.q(css=speed_css).first.click()

    @property
    def get_video_speed(self):
        speed_css = '.speeds p.active'
        return self.q(css=speed_css).text[0]

    def set_captions_visibility_state(self, captions_state):
        """
        Set the video captions visible state.
        :param captions_state: str `opened` or `closed`
        """
        css = '.closed .subtitles'
        if self.q(css=css).present is False:
            if captions_state == 'closed':
                self.q(css='.hide-subtitles').first.click()
        else:
            if captions_state != 'closed':
                self.q(css='.hide-subtitles').first.click()

    @property
    def captions_text(self):
        """
        Extract captions text.
        :return: str
        """
        def _captions_text():
            is_present = self.q(css='.subtitles').present
            result = None

            if is_present:
                result = self.q(css='.subtitles').text[0]

            return is_present, result

        return Promise(_captions_text, 'Captions Text').fulfill()


    def is_aligned(self, is_transcript_visible):
        """
        Check if video is aligned properly.
        :param is_transcript_visible: bool
        :return: bool
        """
        # Width of the video container in css equal 75% of window if transcript enabled
        wrapper_width = 75 if is_transcript_visible else 100
        initial = self.browser.get_window_size()

        self.browser.set_window_size(300, 600)
        real, expected = self.browser.get_window_size()

        width = round(100 * real['width'] / expected['width']) == wrapper_width

        self.browser.set_window_size(600, 300)
        real, expected = self.browser.get_window_size()

        height = abs(expected['height'] - real['height']) <= 5

        # Restore initial window size
        self.browser.set_window_size(
            initial['width'], initial['height']
        )

        return all([width, height])

    def _get(self, url):
        """
        Sends a http get request.
        """
        kwargs = dict()

        session_id = [{i['name']: i['value']} for i in self.browser.get_cookies() if i['name'] == u'sessionid']
        if session_id:
            kwargs.update({
                'cookies': session_id[0]
            })

        response = requests.get(url, **kwargs)
        return response.status_code < 400, response.headers, response.content

    def can_we_download_transcript(self, transcript_format, text_to_search):
        """
        Check if we can download a transcript in format `transcript_format` having text `text_to_search`
        :param transcript_format: `srt` or `txt`
        :param text_to_search: str
        :return: bool
        """

        # check if we transcript with correct format
        if '.' + transcript_format not in self.q(css='.video-tracks .a11y-menu-button').text[0]:
            return False

        formats = {
            'srt': 'application/x-subrip',
            'txt': 'text/plain',
        }

        url = self.q(css=VIDEO_BUTTONS['download_transcript']).attrs('href')[0]
        result, headers, content = self._get(url)

        if result is False:
            return False

        if formats[transcript_format] not in headers.get('content-type', ''):
            return False

        if text_to_search not in content:
            return False

        return True

    def select_transcript_format(self, transcript_format):
        """
        Select transcript with format `transcript_format`
        :param transcript_format: `srt` or `txt`
        :return: bool
        """
        button_selector = '.video-tracks .a11y-menu-button'
        menu_selector = VIDEO_MENUS['download_transcript']

        self.q(css=button_selector).results[0].mouse_over()
        if '...' not in self.q(css=button_selector).text[0]:
            return False

        def _is_ajax_finished():
            return self.browser.execute_script("return jQuery.active") == 0

        menu_items = self.q(css=menu_selector + ' a').results
        for item in menu_items:
            if item.get_attribute('data-value') == transcript_format:
                item.click()
                EmptyPromise(_is_ajax_finished, "Loading more Responses").fulfill()
                break

        if self.q(css=menu_selector + ' .active a').attrs('data-value')[0] != transcript_format:
            return False

        if '.' + transcript_format not in self.q(css=button_selector).text[0]:
            return False

        return True

    def is_menu_exist(self, menu_name):
        """
        Check if menu `menu_name` exists
        :param menu_name: menu name
        :return: bool
        :
        """
        return self.q(css=VIDEO_MENUS[menu_name]).present

    def is_duration_matches(self, time_str):
        """
        Checks if video duration equals to duration calculated from `time_str`
        :param time_str: time string in form 1:23
        :return: bool
        """
        duration_in_seconds = self._parse_time_str(time_str)

        if duration_in_seconds == self.duration:
            return True
        return False

    def select_language(self, code):
        """
        Select captions for language `code`
        :param code: str, two character language code like `en`, `zh`
        :return: bool, True for Success, False for Failure or BrokenPromise
        """

        def _is_ajax_finished():
            return self.browser.execute_script("return jQuery.active") == 0

        EmptyPromise(_is_ajax_finished, "Page load Failed.").fulfill()

        selector = VIDEO_MENUS["language"] + ' li[data-lang-code="{code}"]'.format(code=code)

        self.q(css=VIDEO_BUTTONS["CC"]).results[0].mouse_over()
        self.q(css=selector).first.click()

        if 'active' not in self.q(css=selector).results[0].get_attribute('class'):
            return False

        if len(self.q(css=VIDEO_MENUS["language"] + ' li.active').results) != 1:
            return False

        # Make sure that all ajax requests that affects the display of captions are finished.
        # For example, request to get new translation etc.
        def _is_ajax_finished():
            return self.browser.execute_script("return jQuery.active") == 0

        EmptyPromise(_is_ajax_finished, "Captions Display Finished.").fulfill()

        EmptyPromise(lambda: self.q(css='.subtitles').visible, 'Subtitles Visible.').fulfill()

        return True

    def wait_for_video_player(self):
        """
        Wait until Video Player Rendered Completely.
        """
        video_player_init = '.video-wrapper .spinner'

        def _is_player_initialized():
            spinner = self.q(css=video_player_init).attrs('aria-hidden')
            print >> sys.stderr, 'aria >> ', spinner
            return spinner[0] == 'true'

        EmptyPromise(_is_player_initialized, "Video Player Initialization Failed",
                     try_limit=20, try_interval=30).fulfill()

    def videos_rendered(self, mode):
        """
        Check if all videos are rendered in `mode` mode
        :param mode: str `html5` or `youtube`
        :return: bool
        """
        modes = {
            'html5': 'video',
            'youtube': 'iframe'
        }
        html_tag = modes[mode]

        actual = len(self.q(css='.video {0}'.format(html_tag)).results)
        expected = len(self.q(css='.xmodule_VideoModule').results)

        if actual != expected:
            return False

        return self.q(css='.speed_link').present

    @property
    def captions_visible_state(self):
        """
        Check if captions are shown or not
        :return: bool, False if captions are hidden, True otherwise
        """
        captions_state = self.q(css='div.video.closed').present

        if captions_state is True:  # video does not show the captions
            return False
        else:
            return True

    def check_text_in_captions(self, text_list):
        """
        Check for each text in `text_list` if the text is present in captions for video present at
        index text_list.index(text)
        :param text_list: list containing string items

        """
        captions = self.q(css='.subtitles').text

        if len(text_list) != len(captions):
            return False

        for index, text in enumerate(text_list):
            if text not in captions:
                return False

        return True


