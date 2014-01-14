#pylint: disable=E1103, E1101

import copy
import logging
import re

from django.conf import settings
from django.utils.translation import ugettext as _

from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from django_comment_common.utils import unseed_permissions_roles
from auth.authz import _delete_course_group
from xmodule.modulestore.store_utilities import delete_course
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.draft import DIRECT_ONLY_CATEGORIES

unit_stateById = {}              # dictionary of unit states: key=ID, value=stateString

MIXED_STATE_ICON_STRING = "icon-adjust       unit-status-mixed-state"
ALL_PUBLIC_ICON_STRING  = "icon-circle       unit-status-all-public"
ALL_PRIVATE_ICON_STRING = "icon-circle-blank unit-status-all-private"
NO_UNITS_ICON_STRING = ""

log = logging.getLogger(__name__)

# In order to instantiate an open ended tab automatically, need to have this data
OPEN_ENDED_PANEL = {"name": _("Open Ended Panel"), "type": "open_ended"}
NOTES_PANEL = {"name": _("My Notes"), "type": "notes"}
EXTRA_TAB_PANELS = dict([(p['type'], p) for p in [OPEN_ENDED_PANEL, NOTES_PANEL]])


def delete_course_and_groups(course_id, commit=False):
    """
    This deletes the courseware associated with a course_id as well as cleaning update_item
    the various user table stuff (groups, permissions, etc.)
    """
    module_store = modulestore('direct')
    content_store = contentstore()

    org, course_num, run = course_id.split("/")
    module_store.ignore_write_events_on_courses.append('{0}/{1}'.format(org, course_num))

    loc = CourseDescriptor.id_to_location(course_id)
    if delete_course(module_store, content_store, loc, commit):
        print 'removing forums permissions and roles...'
        unseed_permissions_roles(course_id)

        print 'removing User permissions from course....'
        # in the django layer, we need to remove all the user permissions groups associated with this course
        if commit:
            try:
                _delete_course_group(loc)
            except Exception as err:
                log.error("Error in deleting course groups for {0}: {1}".format(loc, err))


def get_modulestore(category_or_location):
    """
    Returns the correct modulestore to use for modifying the specified location
    """
    if isinstance(category_or_location, Location):
        category_or_location = category_or_location.category

    if category_or_location in DIRECT_ONLY_CATEGORIES:
        return modulestore('direct')
    else:
        return modulestore()


def get_course_location_for_item(location):
    '''
    cdodge: for a given Xmodule, return the course that it belongs to
    NOTE: This makes a lot of assumptions about the format of the course location
    Also we have to assert that this module maps to only one course item - it'll throw an
    assert if not
    '''
    item_loc = Location(location)

    # check to see if item is already a course, if so we can skip this
    if item_loc.category != 'course':
        # @hack! We need to find the course location however, we don't
        # know the 'name' parameter in this context, so we have
        # to assume there's only one item in this query even though we are not specifying a name
        course_search_location = Location('i4x', item_loc.org, item_loc.course, 'course', None)
        courses = modulestore().get_items(course_search_location)

        # make sure we found exactly one match on this above course search
        found_cnt = len(courses)
        if found_cnt == 0:
            raise Exception('Could not find course at {0}'.format(course_search_location))

        if found_cnt > 1:
            raise Exception('Found more than one course at {0}. There should only be one!!! Dump = {1}'.format(course_search_location, courses))

        location = courses[0].location

    return location


def get_course_for_item(location):
    '''
    cdodge: for a given Xmodule, return the course that it belongs to
    NOTE: This makes a lot of assumptions about the format of the course location
    Also we have to assert that this module maps to only one course item - it'll throw an
    assert if not
    '''
    item_loc = Location(location)

    # @hack! We need to find the course location however, we don't
    # know the 'name' parameter in this context, so we have
    # to assume there's only one item in this query even though we are not specifying a name
    course_search_location = Location('i4x', item_loc.org, item_loc.course, 'course', None)
    courses = modulestore().get_items(course_search_location)

    # make sure we found exactly one match on this above course search
    found_cnt = len(courses)
    if found_cnt == 0:
        raise BaseException('Could not find course at {0}'.format(course_search_location))

    if found_cnt > 1:
        raise BaseException('Found more than one course at {0}. There should only be one!!! Dump = {1}'.format(course_search_location, courses))

    return courses[0]


def get_lms_link_for_item(location, preview=False, course_id=None):
    """
    Returns an LMS link to the course with a jump_to to the provided location.

    :param location: the location to jump to
    :param preview: True if the preview version of LMS should be returned. Default value is false.
    :param course_id: the course_id within which the location lives. If not specified, the course_id is obtained
           by calling Location(location).course_id; note that this only works for locations representing courses
           instead of elements within courses.
    """
    if course_id is None:
        course_id = Location(location).course_id

    if settings.LMS_BASE is not None:
        if preview:
            lms_base = settings.FEATURES.get('PREVIEW_LMS_BASE')
        else:
            lms_base = settings.LMS_BASE

        lms_link = "//{lms_base}/courses/{course_id}/jump_to/{location}".format(
            lms_base=lms_base,
            course_id=course_id,
            location=Location(location)
        )
    else:
        lms_link = None

    return lms_link


def get_lms_link_for_about_page(location):
    """
    Returns the url to the course about page from the location tuple.
    """
    if settings.FEATURES.get('ENABLE_MKTG_SITE', False):
        if not hasattr(settings, 'MKTG_URLS'):
            log.exception("ENABLE_MKTG_SITE is True, but MKTG_URLS is not defined.")
            about_base = None
        else:
            marketing_urls = settings.MKTG_URLS
            if marketing_urls.get('ROOT', None) is None:
                log.exception('There is no ROOT defined in MKTG_URLS')
                about_base = None
            else:
                # Root will be "https://www.edx.org". The complete URL will still not be exactly correct,
                # but redirects exist from www.edx.org to get to the Drupal course about page URL.
                about_base = marketing_urls.get('ROOT')
                # Strip off https:// (or http://) to be consistent with the formatting of LMS_BASE.
                about_base = re.sub(r"^https?://", "", about_base)
    elif settings.LMS_BASE is not None:
        about_base = settings.LMS_BASE
    else:
        about_base = None

    if about_base is not None:
        lms_link = "//{about_base_url}/courses/{course_id}/about".format(
            about_base_url=about_base,
            course_id=Location(location).course_id
        )
    else:
        lms_link = None

    return lms_link


def course_image_url(course):
    """Returns the image url for the course."""
    loc = course.location._replace(tag='c4x', category='asset', name=course.course_image)
    path = StaticContent.get_url_path_from_location(loc)
    return path


class UnitState(object):
    draft = 'draft'
    private = 'private'
    public = 'public'


def compute_unit_state(unit):
    """
    Returns whether this unit is 'draft', 'public', or 'private'.

    'draft' content is in the process of being edited, but still has a previous
        version visible in the LMS
    'public' content is locked and visible in the LMS
    'private' content is editabled and not visible in the LMS
    """

    if getattr(unit, 'is_draft', False):
        try:
            modulestore('direct').get_item(unit.location)
            return UnitState.draft
        except ItemNotFoundError:
            return UnitState.private
    else:
        return UnitState.public


def update_item(location, value):
    """
    If value is None, delete the db entry. Otherwise, update it using the correct modulestore.
    """
    if value is None:
        get_modulestore(location).delete_item(location)
    else:
        get_modulestore(location).update_item(location, value)


def add_extra_panel_tab(tab_type, course):
    """
    Used to add the panel tab to a course if it does not exist.
    @param tab_type: A string representing the tab type.
    @param course: A course object from the modulestore.
    @return: Boolean indicating whether or not a tab was added and a list of tabs for the course.
    """
    # Copy course tabs
    course_tabs = copy.copy(course.tabs)
    changed = False
    # Check to see if open ended panel is defined in the course

    tab_panel = EXTRA_TAB_PANELS.get(tab_type)
    if tab_panel not in course_tabs:
        # Add panel to the tabs if it is not defined
        course_tabs.append(tab_panel)
        changed = True
    return changed, course_tabs


def remove_extra_panel_tab(tab_type, course):
    """
    Used to remove the panel tab from a course if it exists.
    @param tab_type: A string representing the tab type.
    @param course: A course object from the modulestore.
    @return: Boolean indicating whether or not a tab was added and a list of tabs for the course.
    """
    # Copy course tabs
    course_tabs = copy.copy(course.tabs)
    changed = False
    # Check to see if open ended panel is defined in the course

    tab_panel = EXTRA_TAB_PANELS.get(tab_type)
    if tab_panel in course_tabs:
        # Add panel to the tabs if it is not defined
        course_tabs = [ct for ct in course_tabs if ct != tab_panel]
        changed = True
    return changed, course_tabs



#________________________________________________________
#________________________________________________________
#
# Support for bulk unit status change
#

def get_unit_state_icon_name( unit ):
    """
    Check the supplied unit's public/private/draft state, returning
    a string describing the icon style for the unit
    @param unit: A unit to look up in the dictionary of unit/states
    @return: A string indicating one of three states--mixed, all public, all private.
    """
    return_string = MIXED_STATE_ICON_STRING
    state = compute_unit_state(unit)

    if state == "public":
        return_string = ALL_PUBLIC_ICON_STRING

    if (state == "private") or (state == "draft"):
        return_string = ALL_PRIVATE_ICON_STRING

    return return_string

def get_unit_location(unit):
    #from pdb import set_trace; set_trace()
    return str(unit.location).split("//")[1]

def get_unit_is_private(unit):
    count = 0
    state = compute_unit_state(unit)
    if (state == "private") or (state == "draft"):
        count = 1
    return count


def get_unit_is_public(unit):
    count = 0
    state = compute_unit_state(unit)
    if (state == "public"):
        count = 1
    return count

def _get_subsection_state(subsection):
    """
    Check the indicated subsection's child units, returning
    a set of lists of units in each of the following
    categories:
        public      -- units with status public
        private     -- unit status is private
        found       -- each unit found adds one count

    @param subsection: the subsection whose units are to be analyzed
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created

    unit_count = 0
    subsection_status_string = MIXED_STATE_ICON_STRING
    unit_public_count = 0
    unit_count = 0
    found_items_total = []                            # all units

    for unit in subsection.get_children():
        found_items_total.append(unit)
        if unit_stateById[ unit.location.name ] == "public":
            unit_public_count += 1
        unit_count += 1

    if unit_count == 0:
        subsection_status_string = NO_UNITS_ICON_STRING
    else:
        if unit_count == unit_public_count :
            subsection_status_string = ALL_PUBLIC_ICON_STRING

        if unit_public_count == 0:
            subsection_status_string = ALL_PRIVATE_ICON_STRING

    return unit_count, found_items_total, unit_public_count, subsection_status_string

def get_subsection_state( subsection ):
    unit_count, found_items_total, unit_public_count, subsection_status_string = _get_subsection_state(subsection)
    return subsection_status_string

def get_subsection_public_units_count( subsection ):
    unit_count, found_items_total, unit_public_count, subsection_status_string = _get_subsection_state(subsection)
    return str(unit_public_count)

def get_subsection_private_units_count( subsection ):
    unit_count, found_items_total, unit_public_count, subsection_status_string = _get_subsection_state(subsection)
    private_units_count = unit_count - unit_public_count
    return str(private_units_count)

def get_subsection_total_units_count( subsection ):
    unit_count, found_items_total, unit_public_count, subsection_status_string = _get_subsection_state(subsection)
    return str(unit_count)

def get_subsection_units( subsection ):
    unit_count, found_items_total, unit_public_count, subsection_status_string = _get_subsection_state(subsection)

    unit_locations_string = ""
    for unit in found_items_total:
        unit_locations_string = unit_locations_string + str(unit.location) + ";"
    return unit_locations_string








def get_section_unit_counts_private( section ):
    """
    Check all the units belonging to all subsections, returning
    just the count of the number of private units

    @param section: the section whose units are to be analyzed
    @return: a string -- number of private units found

    NOTE: this function assumes the 'unit_stateById' dictionary has been
    populated before it is called (see 'get_section_unit_states' below)
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created
    found_items_public, found_items_private, found_items_total = _get_section_units( section )
    return str(len(found_items_private))

def get_section_unit_counts_public( section ):
    """
    Check all the units belonging to all subsections, returning
    just the count of the number of public units

    @param section: the section whose units are to be analyzed
    @return: a string -- number of public units found

    NOTE: this function assumes the 'unit_stateById' dictionary has been
    populated before it is called (see 'get_section_unit_states' below)
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created
    found_items_public, found_items_private, found_items_total = _get_section_units( section )
    return str(len(found_items_public))

def get_section_unit_counts_found( section ):
    """
    Check all the units belonging to all subsections, returning
    just the count of the number of found units

    @param section: the section whose units are to be analyzed
    @return: a string -- number of units found

    NOTE: this function assumes the 'unit_stateById' dictionary has been
    populated before it is called (see 'get_section_unit_states' below)
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created
    found_items_public, found_items_private, found_items_total = _get_section_units( section )
    return str(len(found_items_total))


# experimental
def get_section_units( section ):
    """
    Check all the units belonging to all subsections, returning
    just the count of the number of found units

    @param section: the section whose units are to be analyzed
    @return: a string -- number of units found

    NOTE: this function assumes the 'unit_stateById' dictionary has been
    populated before it is called (see 'get_section_unit_states' below)
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created
    found_items_public, found_items_private, found_items_total = _get_section_units( section )

    unit_locations_string = ""
    for unit in found_items_total:
        unit_locations_string = unit_locations_string + str(unit.location) + ";"

    return unit_locations_string






def _get_section_units( section ):
    """
    Check all the units belonging to all subsections, returning
    a set of lists of units in each of the following
    categories:
        public      -- units with status public
        private     -- unit status is private
        found       -- each unit found adds one count

    @param section: the section whose units are to be analyzed
    @return: 3 lists -- public, private, and found units

    NOTE: this function assumes the 'unit_stateById' dictionary has been
    populated before it is called (see 'get_section_unit_states' below)
    """
    assert unit_stateById.__sizeof__() > 0  # be sure the dictionary of unit/state has been created

    found_items_private = []                          # private units
    found_items_public = []                           # public units
    found_items_total = []                            # all units

    for subsection in section.get_children():
      for unit in subsection.get_children():
        found_items_total.append(unit)
        state = compute_unit_state(unit)
        unit_stateById[ unit.location.name ] = state

        if state == "public":
            found_items_public.append(unit)

        if (state == "private") or (state == "draft"):
            found_items_private.append(unit)

    return found_items_public, found_items_private, found_items_total


def get_section_unit_states( section ):
    """
    Check all the units belonging to all subsections, returning
    a string describing the style for the icon to show. Note that
    a dictionary of unit/state entries is created by this function
    to be used by other functions found in this file. Thus, this
    function must be run first, before those other functions can
    be safely called.
    """
    return_string = MIXED_STATE_ICON_STRING
    found_items_private = 0                           # counts the number of private units
    found_items_public = 0                            # counts the number of public units
    found_items_total = 0                             # counts the total number of units

    for subsection in section.get_children():
      found_items_private_subsection = 0              # counts the number of private units in this subsection
      found_items_public_subsection = 0               # counts the number of public units in this subsection
      found_items_total_subsection = 0                # counts the total number of units in this subsection

      for unit in subsection.get_children():
        found_items_total_subsection += 1
        found_items_total += 1
        state = compute_unit_state(unit)
        unit_stateById[ unit.location.name ] = state

        if state == "public":
            found_items_public += 1
            found_items_public_subsection += 1

        if (state == "private") or (state == "draft"):
            found_items_private += 1
            found_items_private_subsection += 1

    if found_items_public == found_items_total:
        return_string = ALL_PUBLIC_ICON_STRING

    if found_items_public == 0:
        return_string = ALL_PRIVATE_ICON_STRING

    return return_string + " unit-status-section-icon-adjustment"


