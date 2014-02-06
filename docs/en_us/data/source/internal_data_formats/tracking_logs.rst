######################
Tracking Logs
######################

The following is an inventory of all LMS event types. **Question**: is this really of LMS event types only?

This inventory is comprised of a table of Common Fields that appear in all events, a table of Student Event Types which lists all interaction with the LMS outside of the Instructor Dashboard,
and a table of Instructor Event Types of all interaction with the Instructor Dashboard in the LMS.

In the data package, events are delivered in a log file. 

.. _sample:

*************************
Sample Events
*************************

Two sample events from the edX/prod-edxapp-011/2014-01-26_edX.log file follows.

    {"username": "*username*", "event_type": "problem_check", "ip": "*ip_address*", "agent": "Mozilla/5.0 (Windows NT 6.0; rv:20.0) Gecko/20100101 Firefox/20.0", "host": "courses.edx.org", "session": "1cc603b3b4b2ed9a5475511d5d974658", "event": "\"input_i4x-edX-DemoX-problem-c554538a57664fac80783b99d9d6da7c_2_1=%5B828%2C653%5D\"", "event_source": "browser", "context": {"course_id": "edX/DemoX/Demo_Course", "org_id": "edX", "user_id": 3312650}, "time": "2014-01-26T00:00:25.776429+00:00", "page": "https://courses.edx.org/courses/edX/DemoX/Demo_Course/courseware/interactive_demonstrations/basic_questions/"}

    {"username": "*user_name*", "host": "courses.edx.org", "event_source": "server", "event_type": "/courses/edX/DemoX/Demo_Course/xblock/i4x:;_;_edX;_DemoX;_problem;_c554538a57664fac80783b99d9d6da7c/handler/xmodule_handler/problem_check", "context": {"course_id": "edX/DemoX/Demo_Course", "org_id": "edX", "user_id": *id*}, "time": "2014-01-26T00:00:25.781622+00:00", "ip": "*ip_address*", "event": "{\"POST\": {\"input_i4x-edX-DemoX-problem-c554538a57664fac80783b99d9d6da7c_2_1\": [\"[828,653]\"]}, \"GET\": {}}", "agent": "Mozilla/5.0 (Windows NT 6.0; rv:20.0) Gecko/20100101 Firefox/20.0", "page": null}

.. _common:

********************
Common Fields
********************

This section contains a table of fields common to all events.

+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| Common Field             | Details                                                     | Type        | Values/Format                      |
+==========================+=============================================================+=============+====================================+
| ``agent``                | Browser agent string of the user who triggered the event.   | string      |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``event``                | Specifics of the triggered event.                           | string/JSON |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``event_source``         | Specifies whether the triggered event originated in the     | string      | `'browser'`, `'server'`, `'task'`  |
|                          | browser or on the server.                                   |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``event_type``           | The type of event triggered. Values depend on               | string      | (see below)                        |
|                          | ``event_source``                                            |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``ip``                   | IP address of the user who triggered the event.             | string      |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``page``                 | Page user was visiting when the event was fired.            | string      | `'$URL'`                           |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``session``              | This key identifies the user's session. May be undefined.   | string      | 32 digits                          |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``time``                 | Gives the GMT time at which the event was fired.            | string      | `'YYYY-MM-DDThh:mm:ss.xxxxxx'`     |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| ``username``             | The username of the user who caused the event to fire. This | string      |                                    |
|                          | string is empty for anonymous events (i.e., user not logged |             |                                    |
|                          | in).                                                        |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| host                     | TBD                                                         |             |                                    |
|                          |                                                             |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| user_id                  | TBD                                                         |             |                                    |
|                          |                                                             |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+
| context                  | TBD                                                         |             |                                    |
|                          |                                                             |             |                                    |
+--------------------------+-------------------------------------------------------------+-------------+------------------------------------+


********************
Event Types
********************

There are two tables of event types -- one for student events, and one for instructor events. Table columns describe what each event type represents, which component it originates from, what scripting language was used to fire the event, and what ``event`` fields are associated with it. The ``event_source`` field from the "Common Fields" table above distinguishes between events that originated in the browser (in javascript) and events that originated on the server (during the processing of a request).

Event types with several different historical names are enumerated by forward slashes. Rows identical after the second column have been combined, with the corresponding event types enumerated by commas.

=========================
Enrollment Event Types
=========================

TBD --- is this edX registration or course registration? 

Event Source for Both is Server

* edx.course.enrollment.activated

* edx.course.enrollment.deactivated

TBD

==================================================
Student Event Types
==================================================

The Student Event Type table lists the event types logged for interaction with the LMS outside the Instructor Dashboard.

* :ref:`nav`

* :ref:`hide`

* :ref:`show`

* :ref:`rubric_select`

TBD

.. _nav:

=============================
Navigational Event Types   
=============================

These event types are fired when a user selects a navigational control. **Question:** what does a "sequence" correspond to in Studio? a subsection?

* ``seq_goto`` is fired when a user jumps between units in a sequence. 

* ``seq_next`` is fired when a user navigates to the next unit in a sequence. 

* ``seq_prev`` is fired when a user navigates to the previous unit in a sequence. 

**Component**: Sequence

**Event Source**: Browser

``event`` **Fields**: 

+--------------------+---------------+---------------------------------------------------------------------+
| Field              | Type          | Details                                                             |
+====================+===============+=====================================================================+
| ``old``            | integer       | For ``seq_goto``, the index of the unit being jumped from.          |
|                    |               | For ``seq_next`` and ``seq_prev``, the index of the unit being      |
|                    |               | navigated away from.                                                |
+--------------------+---------------+---------------------------------------------------------------------+
| ``new``            | integer       | For ``seq_goto``, the index of the unit being jumped to.            |
|                    |               | For ``seq_next`` and ``seq_prev``, the index of the unit being      |
|                    |               | navigated to.                                                       |
+--------------------+---------------+---------------------------------------------------------------------+
| ``id``             | integer       | The edX ID of the sequence.                                         |
+--------------------+---------------+---------------------------------------------------------------------+


.. _hide:

------------------------------------------------
``hide`` Event Types
------------------------------------------------

**Description**: 

.. TBD

**Question** this was a list of 6 event_types, separated by slashes, as though 5 were deprecated and one was still in use. Correct? which is still in use? when was there a change? (or is it that for 3 different event_types a change was made from "question" to "problem"?)

+---------------------------------+----------------------------------------+
| Event Type                      | Component                              |
+=================================+========================================+
| ``oe_hide_question``            | Combined Open-Ended                    |
+---------------------------------+----------------------------------------+
| ``oe_hide_problem``             | Combined Open-Ended                    |
+---------------------------------+----------------------------------------+
| ``peer_grading_hide_question``  | Peer Grading                           |  
+---------------------------------+----------------------------------------+
| ``peer_grading_hide_problem``   | Peer Grading                           | 
+---------------------------------+----------------------------------------+
| ``staff_grading_hide_question`` | Staff Grading                          | 
+---------------------------------+----------------------------------------+
| ``staff_grading_hide_problem``  | Staff Grading                          | 
+---------------------------------+----------------------------------------+

**Event Source**: Browser

``event`` **Fields**: 

+--------------------+---------------+---------------------------------------------------------------------+
| Field              | Type          | Details                                                             |
+====================+===============+=====================================================================+
| ``location``       | string        | The location of the question whose prompt is                        |
|                    |               | being hidden.                                                       |
+--------------------+---------------+---------------------------------------------------------------------+

.. _show:

------------------------------------------------
``show`` Event Types
------------------------------------------------

**Description**: 

.. TBD

**Question** same as above

+---------------------------------+----------------------------------------+
|Event Type                       | Component                              |
+=================================+========================================+
| ``oe_show_question``            | Combined Open-Ended                    |
+---------------------------------+----------------------------------------+
| ``oe_show_problem``             | Combined Open-Ended                    |
+---------------------------------+----------------------------------------+
| ``peer_grading_show_question``  | Peer Grading                           |  
+---------------------------------+----------------------------------------+
| ``peer_grading_show_problem``   | Peer Grading                           | 
+---------------------------------+----------------------------------------+
| ``staff_grading_show_question`` | Staff Grading                          | 
+---------------------------------+----------------------------------------+
| ``staff_grading_show_problem``  | Staff Grading                          | 
+---------------------------------+----------------------------------------+

**Event Source**: Browser

``event`` **Fields**: 

+--------------------+---------------+---------------------------------------------------------------------+
| Field              | Type          | Details                                                             |
+====================+===============+=====================================================================+
| ``location``       | string        | The location of the question whose prompt is                        |
|                    |               | being shown.                                                        |
+--------------------+---------------+---------------------------------------------------------------------+

.. _rubric_select:

------------------------------------------------
``rubric_select`` Event Type   
------------------------------------------------

**Description**: 

.. TBD

**Component**: Combined Open-Ended

**Event Source**: Browser

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``location``        | string        | The location of the question whose rubric is                        |
|                     |               | being selected.                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``selection``       | integer       | Value selected on rubric.                                           |
+---------------------+---------------+---------------------------------------------------------------------+
| ``category``        | integer       | Rubric category selected.                                           |
+---------------------+---------------+---------------------------------------------------------------------+


.. _oe_show:

------------------------------------------------
``oe_show_*_feedback`` Event Types
------------------------------------------------

**Description**: 

.. TBD

``oe_show_full_feedback``

``oe_show_respond_to_feedback`` 

**Question** these were not separated by / or , -- are they two different valid event types, or is one deprecated?

**Component**: Combined Open-Ended

**Event Source**: Browser

``event`` **Fields**: None

.. _oe_feedback:

------------------------------------------------
``oe_feedback_response_selected`` Event Type
------------------------------------------------

**Description**: 

.. TBD

**Component**: Combined Open-Ended

**Event Source**: Browser

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``value``           | integer       | Value selected in the feedback response form.                       |
+---------------------+---------------+---------------------------------------------------------------------+

.. _page_close:

------------------------------------------------
``page_close`` Event Type
------------------------------------------------

**Description**: This event type originates from within the Logger itself.

**Component**: Logger

**Event Source**: Browser

``event`` **Fields**: None

.. _video:

------------------------------------------------
``*_video`` Event Types  
------------------------------------------------

**Description**: The ``play_video`` event type is fired on video play. The ``pause_video`` event type is fired on video pause. 

**Component**: Video

**Event Source**: Browser

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``id``              | string        | EdX ID of the video being watched (for example,                     |
|                     |               | i4x-HarvardX-PH207x-video-Simple_Random_Sample).                    |
+---------------------+---------------+---------------------------------------------------------------------+
| ``code``            | string        | YouTube ID of the video being watched (for                          |
|                     |               | example, FU3fCJNs94Y).                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``currentTime``     | float         | Time the video was played at, in seconds.                           |
+---------------------+---------------+---------------------------------------------------------------------+
| ``speed``           | string        | Video speed in use (i.e., 0.75, 1.0, 1.25, 1.50).                   |
|                     |               | **Question**: did the speed_change_video e_type replace this?       |
+---------------------+---------------+---------------------------------------------------------------------+

ADDITIONAL VIDEO EVENT_TYPES:

* ``speed_change_video`` TBD

* ``hide_transcript`` TBD

* ``show_transcript`` TBD

* ``load_video`` TBD

* ``seek_video`` TBD

    {
                old_time: this.videoPlayer.currentTime,
                new_time: newTime,
                type: params.type
            }


.. _book:

------------------------------------------------
Book (PDF) Event Type   
------------------------------------------------

**Description**: Fired when a user is reading a PDF book.  

**Component**: PDF Viewer 

**Event Source**: Browser

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``type``            | string        | `'gotopage'`, `'prevpage'`, `'nextpage'`                            |
+---------------------+---------------+---------------------------------------------------------------------+
| ``old``             | integer       | Original page number.                                               |
+---------------------+---------------+---------------------------------------------------------------------+
| ``new``             | integer       | Destination page number.                                            |
+---------------------+---------------+---------------------------------------------------------------------+

.. _problem_check:

------------------------------------------------
``problem_check`` Event Type   
------------------------------------------------

**Description**: Fired when a user wants to check a problem.  

**Component**: Capa Module

**Event Source**: Browser

``event`` **Fields**: The ``event`` field contains the values of all input fields from the problem being checked, styled as GET parameters.

.. _save_problem:

----------------------------------------------------------
``problem_check`` / ``save_problem_check`` Event Types   
----------------------------------------------------------

**Description**: Fired when a problem has been checked successfully. 

**Question**: is one of these deprecated? which one? (Ideally, when?) do any of these fields relate to one of them only?

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being checked.                                    |
+---------------------+---------------+---------------------------------------------------------------------+
| ``answers``         | dict          |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``success``         | string        | `'correct'`, `'incorrect'`                                          |
+---------------------+---------------+---------------------------------------------------------------------+
| ``attempts``        | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``grade``           | integer       | Current grade value                                                 |
+---------------------+---------------+---------------------------------------------------------------------+
| ``max_grade``       | integer       | Maximum possible grade value                                        |
+---------------------+---------------+---------------------------------------------------------------------+
| ``correct_map``     | string / JSON | A table of ``correct_map`` field types and values follows.          |
+---------------------+---------------+---------------------------------------------------------------------+

.. _correct_map:

``correct_map`` *Fields and Values**

+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``correct_map`` Field              | Type                     | Values / Format                                  |  Null Allowed?    |
+====================================+==========================+==================================================+===================+
| ``answer_id``                      | string                   |                                                  |                   |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``correctness``                    | string                   | `'correct'`, `'incorrect'`                       |                   |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``npoints``                        | integer                  | Points awarded for this ``answer_id``.           | yes               |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``msg``                            | string                   | Gives extra message response.                    |                   |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``hint``                           | string                   | Gives optional hint.                             | yes               |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``hintmode``                       | string                   | None, `'on_request'`, `'always'`                 | yes               |
+------------------------------------+--------------------------+--------------------------------------------------+-------------------+
| ``queuestate``                     | dict                     | None when not queued, else `{key:' ', time:' '}` | yes               |
|                                    |                          | where key is a secret string and time is a       |                   |
|                                    |                          | string dump of a DateTime object of the form     |                   |
|                                    |                          | `'%Y%m%d%H%M%S'`.                                |                   |
+------------------------------------+--------------------------------------------------+--------------------------+-------------------+

.. _problem_check_fail:

------------------------------------------------
 ``problem_check_fail`` Event Type   
------------------------------------------------

**Description**: Fired when a problem cannot be checked successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being checked.                                    |
+---------------------+---------------+---------------------------------------------------------------------+
| ``answers``         | dict          |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``failure``         | string        | `'closed'`, `'unreset'`                                             |
+---------------------+---------------+---------------------------------------------------------------------+

------------------------------------------------
``problem_graded`` Event Type
------------------------------------------------

TBD

.. _problem_reset:

------------------------------------------------
``problem_reset`` Event Type   
------------------------------------------------

**Description**: Fired when a user resets a problem. 

**Component**: Capa Module

**Event Source**: Browser

``event`` **Fields**: None

.. _problem_rescore:

----------------------------------------------------------
``problem_rescore`` Event Type 
----------------------------------------------------------

**Description**: Fired when a problem is rescored sucessfully.    

**Question**: why do we have a second description for the same "problem_check" event type? is it really the same name?

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being rescored.                                   |
+---------------------+---------------+---------------------------------------------------------------------+
| ``orig_score``      | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``orig_total``      | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``new_score``       | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``new_total``       | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``correct_map``     | string / JSON | See the table of ``correct_map`` field types and values above.      |
+---------------------+---------------+---------------------------------------------------------------------+
| ``success``         | string        | `'correct'`, `'incorrect'`                                          |
+---------------------+---------------+---------------------------------------------------------------------+
| ``attempts``        | integer       |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _problem_rescore_fail:

------------------------------------------------
 ``problem_rescore_fail`` Event Type   
------------------------------------------------

**Description**: Fired when a problem cannot be rescored successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being rescored.                                   |
+---------------------+---------------+---------------------------------------------------------------------+
| ``failure``         | string        | `'unsupported'`, `'unanswered'`, `'input_error'`, `'unexpected'`    |
+---------------------+---------------+---------------------------------------------------------------------+

.. _problem_show:

------------------------------------------------
``problem_show`` Event Type   
------------------------------------------------

**Description**: Fired when a problem is shown.

**Component**: Capa Module

**Event Source**: Browser

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``problem``         | string        | ID of the problem being shown (e.g.,                                |
|                     |               | i4x://MITx/6.00x/problem/L15:L15_Problem_2).                        |
+---------------------+---------------+---------------------------------------------------------------------+

.. _problem_save:

------------------------------------------------
``problem_save`` Event Type   
------------------------------------------------

**Description**: Fired when a problem is saved.

**Component**: Capa Module

**Event Source**: Browser

``event`` **Fields**: None

.. _reset_problem:

------------------------------------------------
 ``reset_problem`` Event Type   
------------------------------------------------

**Description**: Fired when a problem has been reset successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``old_state``       | string / JSON | Current problem state. **Question** is this really current?         |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being reset.                                      |
+---------------------+---------------+---------------------------------------------------------------------+
| ``new_state``       | string / JSON | New problem state.                                                  |
+---------------------+---------------+---------------------------------------------------------------------+

.. _reset_problem_fail:

------------------------------------------------
 ``reset_problem_fail`` Event Type   
------------------------------------------------

**Description**: Fired when a problem cannot be reset successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``old_state``       | string / JSON | Current problem state. **Question** is this really current?         |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being reset.                                      |
+---------------------+---------------+---------------------------------------------------------------------+
| ``failure``         | string        | `'closed'`, `'not_done'`                                            |
+---------------------+---------------+---------------------------------------------------------------------+

.. _show_answer:

------------------------------------------------
``showanswer`` and ``show_answer`` Event Types   
------------------------------------------------

**Description**: Server-side event which displays the answer to a problem. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``problem_id``      | string        | EdX ID of the problem being shown.                                  |
+---------------------+---------------+---------------------------------------------------------------------+

.. _save_problem_fail:

------------------------------------------------
 ``save_problem_fail`` Event Type   
------------------------------------------------

**Description**: Fired when a problem cannot be saved successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being saved.                                      |
+---------------------+---------------+---------------------------------------------------------------------+
| ``failure``         | string        | `'closed'`, `'done'`                                                |
+---------------------+---------------+---------------------------------------------------------------------+
| ``answers``         | dict          |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _save_problem_success:

------------------------------------------------
 ``save_problem_success`` Event Type   
------------------------------------------------

**Description**: Fired when a problem has been saved successfully. 

**Component**: Capa Module

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``state``           | string / JSON | Current problem state.                                              |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem_id``      | string        | ID of the problem being saved.                                      |
+---------------------+---------------+---------------------------------------------------------------------+
| ``answers``         | dict          |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

------------------------------------------------
Additional Event Types TBD
------------------------------------------------

These were on Brian's list from AN-462, not even sure if they're explicit or implicit, or student-initiated or instructor-initiated:

* get-student-progress-page

* open_ended_notifications

* open_ended_problems

* peer_grading

* progress

* staff_grading

* staff_grading-get_problem_list

All with an Event Source of Server

==================================================
Instructor Event Types
==================================================

The Instructor Event Type table lists the event types logged for course team interaction with the Instructor Dashboard in the LMS.

.. _dump:

------------------------------------------------
 ``list_students`` and``dump_*`` Event Types   
------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) have been combined
**Description**: 

* ``list-students``

* ``dump-grades``

* ``dump-grades-raw``

* ``dump-grades-csv``

* ``dump-grades-csv-raw``

* ``dump-answer-dist-csv``

* ``dump-graded-assignments-config``

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: None

.. _rescore_all:

-----------------------------------------------------------------------
 ``rescore-all-submissions`` and ``reset-all-attempts`` Event Types   
-----------------------------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``problem``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``course``          | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _rescore_student:

-----------------------------------------------------------------------------------
 ``delete-student-module-state`` and ``rescore-student-submission`` Event Types   
-----------------------------------------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``problem``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``student``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``course``          | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _reset_attempts:

-----------------------------------------------------------------------------------
 ``reset-student-attempts`` Event Type
-----------------------------------------------------------------------------------

**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``old_attempts``    | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``student``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``problem``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``instructor``      | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _progress:

-----------------------------------------------------------------------------------
 ``get-student-progress-page`` Event Type
-----------------------------------------------------------------------------------

**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``student``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``instructor``      | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``course``          | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _list_staff:

------------------------------------------------
 ``list-staff`` Event Types   
------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

* ``list-staff``

* ``list-instructors``

* ``list-beta-testers``

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: None

.. _instructor:

------------------------------------------------
 ``*_instructor`` Event Types   
------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

* ``add-instructor``

* ``remove-instructor``

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``instructor``      | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _list_forum:

------------------------------------------------
 ``list_forum_*`` Event Types   
------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

* ``list-forum-admins``

* ``list-forum-mods``

* ``list-forum-community-TAs``

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``course``          | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _forum:

------------------------------------------------
 Managing Discussion Staff Event Types   
------------------------------------------------
.. previously a comma-separated list; "Rows identical after the second column" (which means the name and description columns) were combined
**Description**: 

* ``remove-forum-admin``

* ``add-forum-admin``

* ``remove-forum-mod``

* ``add-forum-mod``

* ``remove-forum-community-TA``

* ``add-forum-community-TA``

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``username``        | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``course``          | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _histogram:

-----------------------------------------------------
 ``psychometrics-histogram-generation`` Event Type  
------------------------------------------------------

**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``problem``         | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+

.. _user_group:

-----------------------------------------------------
 ``add-or-remove-user-group`` Event Type  
------------------------------------------------------

**Description**: 

**Component**: Instructor Dashboard

**Event Source**: Server

``event`` **Fields**: 

+---------------------+---------------+---------------------------------------------------------------------+
| Field               | Type          | Details                                                             |
+=====================+===============+=====================================================================+
| ``event_name``      | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``user``            | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
| ``event``           | string        |                                                                     |
+---------------------+---------------+---------------------------------------------------------------------+
