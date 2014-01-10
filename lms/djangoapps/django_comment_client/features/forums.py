import re

from lettuce import world, step

from django_comment_common.utils import seed_permissions_roles


@step(u'I visit the discussion tab')
def visit_the_discussion_tab(step):
    create_course()
    world.register_by_course_id('edx/999/Test_Course')
    world.log_in()
    go_to_discussion_home()

def go_to_discussion_home():
    world.visit('/courses/edx/999/Test_Course/discussion/forum/')
    world.wait_for_js_to_load()

@step(u'I should see the discussion home screen')
def see_discussion_home(step):
    assert world.css_value('.discussion-article .home-header .label') == 'DISCUSSION HOME:'
    assert world.css_value('.discussion-article .home-title') == 'Test Course'

@step(u'I can post, read, and search in the forums with this text:')
def post_read_and_search(step):
    for hash in step.hashes:
        text = hash['text']

        title = 'title: {}'.format(text)
        body = 'body: {}'.format(text)
        response = 'response: {}'.format(text)
        comment = 'comment: {}'.format(text)

        thread_id = _create_thread(title, body)
        response_id = _create_response(thread_id, response)
        comment_id = _create_comment(response_id, comment)

        edited_title = 'edited {}'.format(title)
        edited_body = 'edited {}'.format(body)
        edited_response = 'edited {}'.format(response)

        _edit_thread(thread_id, edited_title, edited_body)
        _edit_response(response_id, edited_response)

        _search_thread_expecting_result(edited_title, edited_title, thread_id)
        _search_thread_expecting_result(edited_body, edited_title, thread_id)
        _search_thread_expecting_result(edited_response, edited_title, thread_id)

        go_to_discussion_home()

def create_course():
    world.clear_courses()
    course = world.scenario_dict['COURSE'] = world.CourseFactory.create(
        org='edx', number='999', display_name='Test Course'
    )
    seed_permissions_roles(course.id)

def _create_thread(title, body, username='robot'):
    world.css_click('.new-post-btn')
    world.css_fill('#new-post-title', title)
    world.css_fill('#wmd-input-new-post-body-undefined', body)
    world.css_click('#new-post-submit')
    world.wait_for_js_to_load()
    assert world.css_value('div.discussion-post h1') == title
    assert world.css_value('div.discussion-post .post-body') == body
    assert world.css_value('div.discussion-post .posted-details .username') == username
    m = re.search(r'\/threads\/([a-z0-9]{24})$', world.browser.url)
    assert m is not None
    thread_id = m.groups()[0]

    # force reload from server and re-check
    world.browser.reload()
    world.wait_for_js_to_load()
    assert world.css_value('div.discussion-post h1') == title
    assert world.css_value('div.discussion-post .post-body') == body
    assert world.css_value('div.discussion-post .posted-details .username') == username
    return thread_id

def _edit_thread(thread_id, title, body, username='robot'):
    # note thread_id is ignored right now; we assume the page is already on the desired thread
    world.css_click('div.discussion-post a.action-edit')
    world.css_fill('input#edit-post-title.edit-post-title', title)
    world.css_fill('textarea#wmd-input-edit-post-body-undefined.wmd-input', body)
    world.css_click('input#edit-post-submit.post-update')
    world.wait_for_js_to_load()
    assert world.css_value('div.discussion-post h1') == title
    assert world.css_value('div.discussion-post .post-body') == body
    assert world.css_value('div.discussion-post .posted-details .username') == username

    # force reload from server and re-check
    world.browser.reload()
    world.wait_for_js_to_load()
    assert world.css_value('div.discussion-post h1') == title
    assert world.css_value('div.discussion-post .post-body') == body
    assert world.css_value('div.discussion-post .posted-details .username') == username

def _create_response(thread_id, body, username='robot'):
    world.css_fill('#wmd-input-reply-body-{}'.format(thread_id), body)
    world.css_click('.discussion-submit-post.control-button')
    world.wait_for_js_to_load()
    assert world.css_value('.discussion-response .response-body p') == body

    # force reload from server and re-check (also, get the real server-assigned id)
    world.browser.reload()
    world.wait_for_js_to_load()
    assert world.css_value('.discussion-response .response-body p') == body
    response_id = world.browser.evaluate_script("$('div#add-new-comment')[0].attributes['data-id'].value")
    return response_id

def _edit_response(response_id, body, username='robot'):
    # again, not using response_id to locate the response;
    # just assume it's the first/only one on the current screen
    world.css_click('div.discussion-response a.action-edit')
    world.css_fill('textarea#wmd-input-edit-post-body-undefined.wmd-input', body)
    world.css_click('INPUT#edit-response-submit.post-update')
    world.wait_for_js_to_load()
    assert world.css_value('.discussion-response .response-body p') == body

    # force reload from server and re-check (also, get the real server-assigned id)
    world.browser.reload()
    world.wait_for_js_to_load()
    assert world.css_value('.discussion-response .response-body p') == body
    

def _create_comment(response_id, body, username='robot'):
    world.css_click('#wmd-input-comment-body-{}'.format(response_id))
    world.css_fill('#wmd-input-comment-body-{}'.format(response_id), body)
    world.css_click('a.discussion-submit-comment.control-button')
    world.wait_for_js_to_load()
    assert world.css_text('ol.comments div.response-body p') == body

    # force reload from server and re-check (also, get the real server-assigned id)
    world.browser.reload()
    world.wait_for_js_to_load()
    assert world.css_text('ol.comments div.response-body p') == body


def _search_thread_expecting_result(text, title, thread_id):
    world.css_click('FORM.post-search')
    # world.css_fill not working correctly with the forums search input, bypassing.
    world.browser.find_by_css('INPUT#search-discussions.post-search-field').first.fill('{}\r'.format(text))
    world.wait_for_ajax_complete()
    assert world.css_text('ul.post-list a[data-id="{}"] span.title'.format(thread_id)) == title

