from lettuce import world, step

from django_comment_common.utils import seed_permissions_roles

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
