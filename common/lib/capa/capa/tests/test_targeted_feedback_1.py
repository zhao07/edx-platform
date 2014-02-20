"""
Tests the logic of the "targeted-feedback" attribute for MultipleChoice questions,
i.e. those with the <multiplechoiceresponse> element

NOTE: this file includes code which is about to be pulled into `master` in a file
called `test_targeted_feedback.py`. Once both files are brought to `master` this
one should be merged in to the original then discarded.

"""

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

    def test_no_targeted_feedback(self):
        xml_str = textwrap.dedent("""
            <problem>
            <p>What is the correct answer?</p>
            <multiplechoiceresponse>
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<div>.*'wrong-1'.*'wrong-2'.*'correct-1'.*'wrong-3'.*</div>")
        self.assertRegexpMatches(without_new_lines, r"feedback1|feedback2|feedback3|feedbackC")

    def test_targeted_feedback_not_finished(self):
        xml_str = textwrap.dedent("""
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<div>.*'wrong-1'.*'wrong-2'.*'correct-1'.*'wrong-3'.*</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback1|feedback2|feedback3|feedbackC")
        self.assertEquals(the_html, problem.get_html(), "Should be able to call get_html() twice")

    def test_targeted_feedback_student_answer1(self):
        xml_str = textwrap.dedent("""
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_3'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedback3\">.*3rd WRONG solution")
        self.assertNotRegexpMatches(without_new_lines, r"feedback1|feedback2|feedbackC")
        # Check that calling it multiple times yields the same thing
        the_html2 = problem.get_html()
        self.assertEquals(the_html, the_html2)

    def test_targeted_feedback_student_answer2(self):
        xml_str = textwrap.dedent("""
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_0'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedback1\">.*1st WRONG solution")
        self.assertRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback2|feedback3|feedbackC")

    def test_targeted_feedback_show_solution_explanation(self):
        xml_str = textwrap.dedent("""
            <problem>
            <p>What is the correct answer?</p>
            <multiplechoiceresponse targeted-feedback="alwaysShowCorrectChoiceExplanation">
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_0'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedback1\">.*1st WRONG solution")
        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedbackC\".*solution explanation")
        self.assertNotRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback2|feedback3")
        # Check that calling it multiple times yields the same thing
        the_html2 = problem.get_html()
        self.assertEquals(the_html, the_html2)

    def test_targeted_feedback_no_show_solution_explanation(self):
        xml_str = textwrap.dedent("""
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solution explanation-id="feedbackC">
            <div class="detailed-solution">
                <p>Explanation</p>
                <p>This is the solution explanation</p>
                <p>Not much to explain here, sorry!</p>
            </div>
            </solution>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_0'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedback1\">.*1st WRONG solution")
        self.assertNotRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedbackC\".*solution explanation")
        self.assertRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback2|feedback3|feedbackC")

    def test_targeted_feedback_with_solutionset_explanation(self):
        xml_str = textwrap.dedent("""
            <problem>
            <p>What is the correct answer?</p>
            <multiplechoiceresponse targeted-feedback="alwaysShowCorrectChoiceExplanation">
              <choicegroup type="MultipleChoice">
                <choice correct="false" explanation-id="feedback1">wrong-1</choice>
                <choice correct="false" explanation-id="feedback2">wrong-2</choice>
                <choice correct="true" explanation-id="feedbackC">correct-1</choice>
                <choice correct="false" explanation-id="feedback3">wrong-3</choice>
                <choice correct="true" explanation-id="feedbackC2">correct-2</choice>
              </choicegroup>
            </multiplechoiceresponse>

            <targetedfeedbackset>
                <targetedfeedback explanation-id="feedback1">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback2">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 2nd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on your correct solution...</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC2">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
                    <p>Feedback on the other solution...</p>
                </div>
                </targetedfeedback>

            </targetedfeedbackset>

            <solutionset>
                <solution explanation-id="feedbackC2">
                <div class="detailed-solution">
                    <p>Explanation</p>
                    <p>This is the other solution explanation</p>
                    <p>Not much to explain here, sorry!</p>
                </div>
                </solution>
            </solutionset>
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_0'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedback1\">.*1st WRONG solution")
        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedbackC2\".*other solution explanation")
        self.assertNotRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback2|feedback3")

    def test_targeted_feedback_no_feedback_for_selected_choice1(self):
        xml_str = textwrap.dedent("""
            <problem>
            <p>What is the correct answer?</p>
            <multiplechoiceresponse targeted-feedback="alwaysShowCorrectChoiceExplanation">
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
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
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_1'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedbackC\".*solution explanation")
        self.assertNotRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback1|feedback3")

    def test_targeted_feedback_no_feedback_for_selected_choice2(self):
        xml_str = textwrap.dedent("""
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
                    <p>Targeted Feedback</p>
                    <p>This is the 1st WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedback3">
                <div class="detailed-targeted-feedback">
                    <p>Targeted Feedback</p>
                    <p>This is the 3rd WRONG solution</p>
                </div>
                </targetedfeedback>

                <targetedfeedback explanation-id="feedbackC">
                <div class="detailed-targeted-feedback-correct">
                    <p>Targeted Feedback</p>
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
        </problem>

        """)

        problem = new_loncapa_problem(xml_str)
        problem.done = True
        problem.student_answers = {'1_2_1': 'choice_1'}

        the_html = problem.get_html()
        without_new_lines = the_html.replace("\n", "")

        self.assertNotRegexpMatches(without_new_lines, r"<targetedfeedback explanation-id=\"feedbackC\".*solution explanation")
        self.assertRegexpMatches(without_new_lines, r"<div>\{.*'1_solution_1'.*\}</div>")
        self.assertNotRegexpMatches(without_new_lines, r"feedback1|feedback3|feedbackC")

    def test_targeted_feedback_xml_from_markdown(self):
        '''
        Verify that a block of XML is manipulated properly according to various conditions
        '''

        xml_str = textwrap.dedent("""
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

        def testCase_01(xml_str):
            '''
            Test Case: targeted feedback is not enabled--could be for any number of reasons
            '''
            problem = new_loncapa_problem(xml_str)
            the_html = problem.get_html(False)      # targeted feedback is not enabled
            without_new_lines = the_html.replace("\n", "")

            testcases = []
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible (testCase_01)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible (testCase_01)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible (testCase_01)"))
            testcases.append((False, r"Incorrect", "no targeted feedback should be shown  (testCase_01)"))
            testcases.append((False, r"Correct", "no targeted feedback should be shown  (testCase_01)"))

            for testcase in testcases:
                expect_match, pattern, message = testcase
                if expect_match:
                    self.assertRegexpMatches(without_new_lines, pattern, message)
                else:
                    self.assertNotRegexpMatches(without_new_lines, pattern, message)

        def testCase_02(xml_str):
            '''
            Test Case: targeted feedback is enabled, but the student has not yet answered
            '''
            problem = new_loncapa_problem(xml_str)
            the_html = problem.get_html(return_true)      # targeted feedback is enabled
            without_new_lines = the_html.replace("\n", "")

            testcases = []
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible (testCase_02)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible (testCase_02)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible (testCase_02)"))
            testcases.append((False, r"Incorrect", "no targeted feedback should be shown (testCase_02)"))
            testcases.append((False, r"Correct", "no targeted feedback should be shown  (testCase_02)"))

            for testcase in testcases:
                expect_match, pattern, message = testcase
                if expect_match:
                    self.assertRegexpMatches(without_new_lines, pattern, message)
                else:
                    self.assertNotRegexpMatches(without_new_lines, pattern, message)

        def testCase_03(xml_str):
            '''
            Test Case: targeted feedback is enabled, the student has answered, but the wrong answer
            '''
            problem = new_loncapa_problem(xml_str)
            problem.done = True                                 # the student has answered
            problem.student_answers = {'1_2_1': 'choice_0'}     # but answered wrong

            the_html = problem.get_html(return_true)      # targeted feedback is enabled
            without_new_lines = the_html.replace("\n", "")

            testcases = []
            testcases.append((True, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should be visible (testCase_03)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible (testCase_03)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should not be visible (testCase_03)"))
            testcases.append((True, r"Incorrect", "incorrect feedback should be shown  (testCase_03)"))
            testcases.append((False, r"Correct", "correct should not be shown (testCase_03)"))
            testcases.append((True, r"This is the 1st WRONG solution", "wrong feedback item shown (testCase_03)"))

            for testcase in testcases:
                expect_match, pattern, message = testcase
                if expect_match:
                    self.assertRegexpMatches(without_new_lines, pattern, message)
                else:
                    self.assertNotRegexpMatches(without_new_lines, pattern, message)

        def testCase_04(xml_str):
            '''
            Test Case: targeted feedback is enabled, the student has answered, and with the right answer
            '''
            problem = new_loncapa_problem(xml_str)
            problem.done = True                                 # the student has answered
            problem.student_answers = {'1_2_1': 'choice_2'}     # but answered wrong

            the_html = problem.get_html(return_true)      # targeted feedback is enabled
            without_new_lines = the_html.replace("\n", "")

            testcases = []
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback1\"", "feedback item `feedback1` should not be visible (testCase_04)"))
            testcases.append((False, r"targetedfeedback explanation-id=\"feedback3\"", "feedback item `feedback3` should not be visible (testCase_04)"))
            testcases.append((True, r"targetedfeedback explanation-id=\"feedbackC\"", "feedback item `feedbackC` should be visible (testCase_04)"))
            testcases.append((False, r"Incorrect", "incorrect feedback should not be shown (testCase_04)"))
            testcases.append((True, r"Correct", "correct should be shown (testCase_04)"))
            testcases.append((True, r"Feedback on your correct solution..", "wrong feedback item shown (testCase_04)"))

            for testcase in testcases:
                expect_match, pattern, message = testcase
                if expect_match:
                    self.assertRegexpMatches(without_new_lines, pattern, message)
                else:
                    self.assertNotRegexpMatches(without_new_lines, pattern, message)

        def return_true():
            '''
            Simply a callable function to return True, standing in for 'targeted_feedback_available()'
            '''
            return True

        testCase_01(xml_str)
        testCase_02(xml_str)
        testCase_03(xml_str)
        testCase_04(xml_str)
