######################
Discussion Forums Data
######################

Data for the discussions in edX are stored in a MongoDB database as collections of JSON documents. MongoDB is a document-oriented, NoSQL database system. MongoDB is open source, and documentation can be found at docs.mongodb.org/manual/

In the data package, discussion data is delivered in a MONGO file, identified by organization and course, in this format: edX-*organization*-*course*-*source*.mongo. 

The primary collection holding all discussion posts written by users is `contents`. Two different types of objects are stored, representing the three levels of interactions that users can have in a discussion. A `CommentThread` represents a post that opens a new thread, often a student question of some sort. A `Comment` represents a response made directly to the conversation started by a `CommentThread`, and also any comments made on a response.

A sample of the field::value pairs in the mongo file, and descriptions of the attributes that these two types of objects share and that are specific to each type, follows.

*********
Samples
*********

Two sample rows, or documents, from a mongo file of discussion data follow. The first document is for a CommentThread, and the second is of a Comment.

    { "_id" : { "$oid" : "50f1dd4ae05f6d2600000001" }, "_type" : "CommentThread", "anonymous" : false, "anonymous_to_peers" : false, "at_position_list" : [], "author_id" : "*id*", "author_username" : "*username*", "body" : "Welcome to the edX101 forum!\n\nThis forum will be regularly monitored by edX. Please post your questions and comments here. When asking a question, don't forget to search the forum to check whether your question has already been answered.\n\n", "closed" : false, "comment_count" : 0, "commentable_id" : "i4x-edX-edX101-course-How_to_Create_an_edX_Course", "course_id" : "edX/edX101/How_to_Create_an_edX_Course", "created_at" : { "$date" : 1358028106904 }, "last_activity_at" : { "$date" : 1358134464424 }, "tags_array" : [], "title" : "Welcome to the edX101 forum!", "updated_at" : { "$date" : 1358134453862 }, "votes" : { "count" : 1, "down" : [], "down_count" : 0, "point" : 1, "up" : [ "48" ], "up_count" : 1 } }

    { "_id" : { "$oid" : "52e55334299c43be73000032" }, "votes" : { "up" : [], "down" : [], "up_count" : 0, "down_count" : 0, "count" : 0, "point" : 0 }, "visible" : true, "abuse_flaggers" : [], "historical_abuse_flaggers" : [], "parent_ids" : [], "at_position_list" : [], "body" : "That's exactly why I am taking a course now, too. The only problem is that I need to learn how to navigate the system. This Demonstration course is somewhat helpful.\n", "course_id" : "edX/DemoX/Demo_Course", "_type" : "Comment", "endorsed" : false, "anonymous" : false, "anonymous_to_peers" : false, "author_id" : "*id*", "comment_thread_id" : { "$oid" : "52c7363ed891a0bee9000040" }, "author_username" : "*username*", "sk" : "52e55334299c43be73000032", "updated_at" : { "$date" : 1390760756519 }, "created_at" : { "$date" : 1390760756519 } }

Descriptions of the fields that these two types of objects share follow.

*****************
Shared Fields
*****************

Descriptions of the fields that are present for both `CommentThread` and `Comment` objects follow.

`_id`
-----
  The 12-byte MongoDB unique ID for this collection. Like all MongoDB IDs, they are monotonically increasing and the first four bytes are a timestamp. 

`_type`
-------
  `CommentThread` or `Comment` depending on the type of object.

`anonymous`
-----------
  If true, this `Comment` or `CommentThread` will show up as written by anonymous, even to those who have moderator privileges in the forums.

`anonymous_to_peers`
--------------------
  Not used. The idea behind this field was that `anonymous_to_peers = true` would make the the comment appear anonymous to your fellow students, but would allow the course staff to see who you were. However, that was never implemented in the UI, and only `anonymous` is actually used. The `anonymous_to_peers` field is always false.

`at_position_list`
------------------
  No longer used. Child comments (replies) are just sorted by their `created_at` timestamp instead. 

`author_id`
-----------
  The user who wrote this. Corresponds to the user IDs we store in our MySQL database as `auth_user.id`

`author_username`
------------------
  **TBD**

`body`
------
  Text of the comment in Markdown. UTF-8 encoded.

`course_id`
-----------
  The full course_id of the course that this comment was made in, including org and run. This value can be seen in the URL when browsing the courseware section. Example: `BerkeleyX/Stat2.1x/2013_Spring`

`created_at`
------------
  Timestamp in UTC. Example: `ISODate("2013-02-21T03:03:04.587Z")`

`updated_at`
------------
  Timestamp in UTC. Example: `ISODate("2013-02-21T03:03:04.587Z")`

`votes`
-------
  Both `CommentThread` and `Comment` objects support voting. In the user interface, students can vote for posts (CommentThreads) and for responses, but not for the third-level comments made on responses. All `Comment` objects still have this attribute, even though there is no way to actually vote on the comment-level items in the UI. This attribute is a dictionary that has the following inside:

  * `up` = list of User IDs that up-voted this comment or thread.
  * `down` = list of User IDs that down-voted this comment or thread (no longer used).
  * `up_count` = total upvotes received.
  * `down_count` = total downvotes received (no longer used).
  * `count` = total votes cast.
  * `point` = net vote, now always equal to `up_count`.

A user only has one vote per `Comment` or `CommentThread`. Though it's still written to the database, the UI no longer displays an option to downvote anything.

**************************
CommentThread Fields
**************************

The following fields are specific to `CommentThread` objects. Each thread in the forums is represented by one `CommentThread`.

`closed`
--------
  If true, this thread was closed by a forum moderator/admin.

`comment_count`
---------------
  The number of comment replies in this thread. This includes all responses and replies, but does not include the original comment that started the thread. So if we had::

    CommentThread: "What's a good breakfast?"
      * Comment: "Just eat cereal!"
      * Comment: "Try a Loco Moco, it's amazing!"
        * Comment: "A Loco Moco? Only if you want a heart attack!"
        * Comment: "But it's worth it! Just get a spam musubi on the side."

  In that exchange, the `comment_count` for the `CommentThread` is `4`.

`commentable_id`
----------------
  We can attach a discussion to any piece of content in the course, or to top level categories like "General" and "Troubleshooting". When the `commentable_id` is a high level category, it's specified in the course's policy file. When it's a specific content piece (e.g. `600x_l5_p8`, meaning 6.00x, Lecture Sequence 5, Problem 8), it's taken from a discussion module in the course.

`last_activity_at`
------------------
  Timestamp in UTC indicating the last time there was activity in the thread (new posts, edits, etc). Closing the thread does not affect the value in this field. 

`tags_array`
------------
  Meant to be a list of tags that were user definable, but no longer used.

`title`
-------
  Title of the thread, UTF-8 string.

********************
Comment Fields
********************

The following fields are specific to `Comment` objects. A `Comment` is a reply to a `CommentThread` (so an answer to the question), or a reply to another `Comment` (a comment about somebody's answer). It used to be the case that `Comment` replies could nest much more deeply, but we later capped it at just these three levels (question, answer, comment) much in the way that StackOverflow does.

`visible`
----------
  **TBD** true/false

`abuse_flaggers`
--------------------
  **TBD**

`historical_abuse_flaggers`
------------------------------
  **TBD**

`endorsed`
----------
  Boolean value, true if a forum moderator or instructor has marked that this `Comment` is a correct answer for whatever question the thread was asking. Exists for `Comments` that are replies to other `Comments`, but in that case `endorsed` is always false because there's no way to endorse such comments through the UI.

`comment_thread_id`
-------------------
  What `CommentThread` are we a part of? All `Comment` objects have this.

`parent_id`
--------------
  Applies only to comments on a response. The `parent_id` is the `_id` of the response-level `Comment` that this `Comment` is a reply to. Note that this field is only present in a `Comment` that is a reply to another `Comment`; it does not appear in a `Comment` that is a reply to a `CommentThread`.

`parent_ids`
------------
  The `parent_ids` attribute appears in all `Comment` objects, and contains the `_id` of all ancestor comments. Since the UI now prevents comments from being nested more than one layer deep, it will only ever have at most one element in it. If a `Comment` has no parent, it's an empty list.

`sk`
--------------------
  **TBD**

