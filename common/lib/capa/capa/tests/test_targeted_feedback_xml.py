'''
This file contains tests aimed at exercising the XML production mechanism of the
targeted feedback feature.
'''

import unittest
import textwrap
from . import test_capa_system, new_loncapa_problem


class CapaTargetedFeedbackTest(unittest.TestCase):
    '''
    Testing class
    '''

    def setUp(self):
        super(CapaTargetedFeedbackTest, self).setUp()
        self.system = test_capa_system()

    targeted_feedback_xml = textwrap.dedent("""
        <problem>
        <p>What is the correct answer?</p>
        <multiplechoiceresponse targeted-feedback="">
          <choicegroup type="MultipleChoice">
            <choice correct="false" explanation-id="feedback1">wrong-1</choice>
            <choice correct="false" explanation-id="feedback2">wrong-2</choice>
            <choice correct="true" explanation-id="feedbackC">correct-1</choice>
            <choice correct="false" explanation-id="feedback3">wrong-3</choice>
          </choicegroup>
        </multiplechoiceresponse>

        <targetedfeedbackset>
            <targetedfeedback explanation-id="feedback1">
            <div class="detailed-targeted-feedback">
                <p>Incorrect</p>
                <p>This is the 1st WRONG solution</p>
            </div>
            </targetedfeedback>

            <targetedfeedback explanation-id="feedback3">
            <div class="detailed-targeted-feedback">
                <p>Incorrect</p>
                <p>This is the 3rd WRONG solution</p>
            </div>
            </targetedfeedback>

            <targetedfeedback explanation-id="feedbackC">
            <div class="detailed-targeted-feedback-correct">
                <p>Correct</p>
                <p>Feedback on your correct solution...</p>
            </div>
            </targetedfeedback>

        </targetedfeedbackset>

        <solutionset>
            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </solutionset>
    </problem>""")

    def test_show_targeted_feedback_disabled(self):
        '''
        Test Case: targeted feedback is not enabled--could be for any number of reasons
        '''
        problem = new_loncapa_problem(self.targeted_feedback_xml)
        the_html = problem.get_html(False)
        without_new_lines = the_html.replace("\n", "")

        testcases = []
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible"))
        testcases.append((False, r"Incorrect", "no targeted feedback should be shown "))
        testcases.append((False, r"Correct", "no targeted feedback should be shown "))
        testcases.append((True, r"What is the correct answer?", ""))       # this test is included here just to satisfy the coverage test

        for testcase in testcases:
            expect_match, pattern, message = testcase
            if expect_match:
                self.assertRegexpMatches(without_new_lines, pattern, message)
            else:
                self.assertNotRegexpMatches(without_new_lines, pattern, message)

    def test_enabled_not_answered(self):
        '''
        Test Case: targeted feedback is enabled, but the student has not yet answered
        '''
        problem = new_loncapa_problem(self.targeted_feedback_xml)
        the_html = problem.get_html(self._return_true)      # targeted feedback is enabled
        without_new_lines = the_html.replace("\n", "")

        testcases = []
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible"))
        testcases.append((False, r"Incorrect", "no targeted feedback should be shown"))
        testcases.append((False, r"Correct", "no targeted feedback should be shown "))
        testcases.append((True, r"What is the correct answer?", ""))       # this test is included here just to satisfy the coverage test

        for testcase in testcases:
            expect_match, pattern, message = testcase
            if expect_match:
                self.assertRegexpMatches(without_new_lines, pattern, message)
            else:
                self.assertNotRegexpMatches(without_new_lines, pattern, message)

    def test_enabled_answered_incorrect(self):
        '''
        Test Case: targeted feedback is enabled, the student has answered, but the wrong answer
        '''
        problem = new_loncapa_problem(self.targeted_feedback_xml)
        problem.done = True                                 # the student has answered
        problem.student_answers = {'1_2_1': 'choice_0'}     # but answered wrong

        the_html = problem.get_html(self._return_true)      # targeted feedback is enabled
        without_new_lines = the_html.replace("\n", "")

        testcases = []
        testcases.append((True, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible"))
        testcases.append((True, r"Incorrect", "incorrect feedback should be shown "))
        testcases.append((False, r"Correct", "correct should not be shown"))
        testcases.append((True, r"This is the 1st WRONG solution", "wrong feedback item shown"))

        for testcase in testcases:
            expect_match, pattern, message = testcase
            if expect_match:
                self.assertRegexpMatches(without_new_lines, pattern, message)
            else:
                self.assertNotRegexpMatches(without_new_lines, pattern, message)

    def test_enabled_answered_correct(self):
        '''
        Test Case: targeted feedback is enabled, the student has answered, and with the right answer
        '''
        problem = new_loncapa_problem(self.targeted_feedback_xml)
        problem.done = True                                 # the student has answered
        problem.student_answers = {'1_2_1': 'choice_2'}     # but answered wrong

        the_html = problem.get_html(self._return_true)      # targeted feedback is enabled
        without_new_lines = the_html.replace("\n", "")

        testcases = []
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible"))
        testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible"))
        testcases.append((True, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should be visible"))
        testcases.append((False, r"Incorrect", "incorrect feedback should not be shown"))
        testcases.append((True, r"Correct", "correct should be shown"))
        testcases.append((True, r"Feedback on your correct solution..", "wrong feedback item shown"))

        for testcase in testcases:
            expect_match, pattern, message = testcase
            if expect_match:
                self.assertRegexpMatches(without_new_lines, pattern, message)
            else:
                self.assertNotRegexpMatches(without_new_lines, pattern, message)

    def _return_true(self):
        '''
        Simply a callable function to return True, standing in for 'targeted_feedback_available()'
        '''
        return True
