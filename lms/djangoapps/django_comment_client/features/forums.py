import datetime
import json
import threading
import uuid

from lettuce import world, step, before, after

from django_comment_common.utils import seed_permissions_roles
from django_comment_client.tests.mock_cs_server.mock_cs_server import MockCommentServiceServer

CS = None

@before.all
def start_mock_cs_server():
    global CS
    s = CS = MockCommentServiceServer(port_num=4567, response={})
    t = threading.Thread(target=s.serve_forever)
    t.daemon = True
    t.start()

@after.all
def stop_mock_cs_server(step):
    global CS
    CS.shutdown()

@step(u'I visit the discussion tab')
def visit_the_discussion_tab(step):
    create_course()
    world.register_by_course_id('edx/999/Test_Course')
    world.log_in()
    world.visit('/courses/edx/999/Test_Course/discussion/forum/')
    world.wait_for_js_to_load()

@step(u'I should see the discussion home screen')
def see_discussion_home(step):
    assert world.css_value('.discussion-article .home-header .label') == 'DISCUSSION HOME:'
    assert world.css_value('.discussion-article .home-title') == 'Test Course'

@step(u'I can create a new thread')
def create_thread(step):
    world.css_click('.new-post-btn')
    world.css_fill('#new-post-title', 'this is the new post title')
    world.css_fill('#wmd-input-new-post-body-undefined', 'this is the new post body')
    CS._response_str = json.dumps({
        "body": 'this is the new post body',
        "anonymous_to_peers": False,
        "votes": {
            "count": 0,
            "down_count": 0,
            "point": 0,
            "up_count": 0
            },
        "user_id": 1,
        "anonymous": False,
        "title": 'this is the new post title',
        "username": "robot",
        "created_at": datetime.datetime.now().isoformat(),
        "tags": [],
        "updated_at": datetime.datetime.now().isoformat(),
        "commentable_id": world.browser.execute_script('$(".topic")[0].attributes["data-discussion_id"]'),
        "abuse_flaggers": [],
        "comments_count": 0,
        "closed": False,
        "course_id": 'edx/999/Test_Course',
        "at_position_list": [],
        "type": "thread",
        "id": str(uuid.uuid4()).replace('-',''),
        "pinned": False
        })

    world.css_click('#new-post-submit')
    world.wait_for_js_to_load()
    assert world.css_value('div.discussion-post h1') == 'this is the new post title'
    assert world.css_value('div.discussion-post .post-body') == 'this is the new post body'
    assert world.css_value('div.discussion-post .posted-details .username') == 'robot'

def create_course():
    world.clear_courses()
    course = world.scenario_dict['COURSE'] = world.CourseFactory.create(
        org='edx', number='999', display_name='Test Course'
    )
    seed_permissions_roles(course.id)

def create_user_and_visit_course():
    world.register_by_course_id('edx/999/Test_Course')
    world.log_in()
    world.visit('/courses/edx/999/Test_Course/courseware/')
