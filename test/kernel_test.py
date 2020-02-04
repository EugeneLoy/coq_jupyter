import unittest
import jupyter_kernel_test

class KernelTests(jupyter_kernel_test.KernelTests):

    # Required by jupyter_kernel_test.KernelTests:
    kernel_name = "coq"
    language_name = "coq"

    _sum_rhs = iter(range(1, 100))

    def _build_sum_command(self):
        lhs = 100
        rhs = next(self._sum_rhs)
        result = str(lhs + rhs)
        command = "Compute {} + {}.".format(lhs, rhs)
        return (result, command)

    def _execute_cell(self, code):
        self.flush_channels()
        reply, output_msgs = self.execute_helper(code=code)

        self.assertEqual(reply['content']['status'], 'ok')
        self.assertEqual(len(output_msgs), 1)
        self.assertEqual(output_msgs[0]['msg_type'], 'execute_result')
        self.assertIn('text/plain', output_msgs[0]['content']['data'])

        return output_msgs[0]['content']['data']['text/plain']

    def setUp(self):
        self._execute_cell("Reset Initial.")

    def test_coq_jupyter____executing_empty_code____should_not_print_anything(self):
        self.flush_channels()
        reply, output_msgs = self.execute_helper(code="")

        self.assertEqual(reply['content']['status'], 'ok')
        self.assertEqual(len(output_msgs), 0)

    def test_coq_jupyter____executing_code_without_coq_content____should_not_print_anything(self):
        self.flush_channels()
        reply, output_msgs = self.execute_helper(code="\n\r\t \n\r\t ")

        self.assertEqual(reply['content']['status'], 'ok')
        self.assertEqual(len(output_msgs), 0)

    def test_coq_jupyter____executing_one_command____prints_computed_command_result(self):
        (expected_result, command) = self._build_sum_command()
        result = self._execute_cell(command)
        self.assertIn(expected_result, result)

    def test_coq_jupyter____executing_one_command____does_not_print_command(self):
        (expected_result, command) = self._build_sum_command()
        result = self._execute_cell(command)
        self.assertNotIn(command, result)

    def test_coq_jupyter____executing_compute_command_when_not_proving____does_not_print_proving_context(self):
        (expected_result, command) = self._build_sum_command()
        result = self._execute_cell(command)
        self.assertNotIn("proving:", result)
        self.assertNotIn("subgoal", result)

    def test_coq_jupyter____executing_multiple_commands____prints_computed_command_results(self):
        (expected_result1, command1) = self._build_sum_command()
        (expected_result2, command2) = self._build_sum_command()
        result = self._execute_cell(command1 + " " + command2)
        self.assertIn(expected_result1, result)
        self.assertIn(expected_result2, result)

    def test_coq_jupyter____executing_commands_when_proving____prints_proving_context(self):
        result = self._execute_cell("Theorem t1 : True.")
        self.assertIn("1 subgoal", result)
        self.assertIn("Proving: t1", result)

        result = self._execute_cell(self._build_sum_command()[1])
        self.assertIn("1 subgoal", result)
        self.assertIn("Proving: t1", result)

        result = self._execute_cell("Proof. pose (i1 := I).")
        self.assertIn("1 subgoal", result)
        self.assertIn("i1 := I : True", result)
        self.assertIn("Proving: t1", result)

        result = self._execute_cell(self._build_sum_command()[1])
        self.assertIn("1 subgoal", result)
        self.assertIn("i1 := I : True", result)
        self.assertIn("Proving: t1", result)

        result = self._execute_cell("exact i1. Qed.")
        self.assertNotIn("1 subgoal", result)
        self.assertNotIn("No more subgoals", result)
        self.assertNotIn("i1 := I : True", result)
        self.assertNotIn("Proving:", result)

        result = self._execute_cell(self._build_sum_command()[1])
        self.assertNotIn("1 subgoal", result)
        self.assertNotIn("No more subgoals", result)
        self.assertNotIn("i1 := I : True", result)
        self.assertNotIn("proving:", result)

    def test_coq_jupyter____when_proving____prints_most_recent_proving_context_once(self):
        result = self._execute_cell("Theorem t3 : bool. Proof. pose (b1 := true). pose (b2 := false).")
        self.assertEqual(result.count("Proving: t3"), 1, "result: " + repr(result))
        self.assertEqual(result.count("1 subgoal"), 1, "result: " + repr(result))
        self.assertEqual(result.count("No more subgoals"), 0, "result: " + repr(result))
        self.assertEqual(result.count("b1 := true : bool"), 1, "result: " + repr(result))
        self.assertEqual(result.count("b2 := false : bool"), 1, "result: " + repr(result))

        result = self._execute_cell("exact b2.")
        self.assertEqual(result.count("Proving: t3"), 1, "result: " + repr(result))
        self.assertEqual(result.count("1 subgoal"), 0, "result: " + repr(result))
        self.assertEqual(result.count("No more subgoals"), 1, "result: " + repr(result))
        self.assertEqual(result.count("b1 := true : bool"), 0, "result: " + repr(result))
        self.assertEqual(result.count("b2 := false : bool"), 0, "result: " + repr(result))

    def _build_commands_with_error_fixture(self, t_base, t, valid_command_template, invalid_command_template, expected_error_message):
        return (
            "t{}_{}".format(t_base + t, t),
            ["t{}_{}".format(t_base + t, i) for i in (1, 2, 3) if i != t],
            ("t{}_0".format(t_base + t), valid_command_template.format(t_base + t, 0)),
            "\n".join([
                valid_command_template.format(t_base + t, i) if i != t else invalid_command_template.format(t_base + t, i)
                for i in (1, 2, 3)
            ]),
            expected_error_message
        )

    def test_coq_jupyter____executing_commands_with_error____prints_error_and_rolls_back(self):
        cases_with_reference_error = [
            self._build_commands_with_error_fixture(
                3,
                t,
                "Definition t{}_{} := I.",
                "Definition t{}_{} := INVALID_REFERENCE.",
                "Error: The reference INVALID_REFERENCE was not found"
            )
            for t in (1,2,3)
        ]
        cases_with_syntax_error = [
            self._build_commands_with_error_fixture(
                6,
                t,
                "Definition t{}_{} := I.",
                "Definition t{}_{} := (I.",
                "Syntax error: ',' or ')' expected after [constr:operconstr"
            )
            for t in (1,2,3)
        ]
        cases_with_incomplete_command_error = [
            self._build_commands_with_error_fixture(
                9,
                t,
                "Definition t{}_{} := I.",
                "Definition t{}_{} := I",
                "Syntax error: '.' expected after"
            )
            for t in (1,2,3)
        ]
        fixture = cases_with_reference_error + cases_with_syntax_error + cases_with_incomplete_command_error

        for f in range(len(fixture)):
            (invalid_definition, valid_definitions, commited_definition, code, expected_error_message) = fixture[f]

            self._execute_cell(commited_definition[1])

            result = self._execute_cell(code)
            self.assertIn(expected_error_message, result, msg="fixture: {}".format(repr(fixture[f])))

            # verify roll back
            result = self._execute_cell("Print All.")
            self.assertIn(commited_definition[0], result, msg="fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(invalid_definition, result, msg="fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(valid_definitions[0], result, msg="fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(valid_definitions[1], result, msg="fixture: {}".format(repr(fixture[f])))

    def test_coq_jupyter____when_executing_command_that_results_in_warning____prints_warning(self):
        # this test ensures fix of the following:
        # https://github.com/EugeneLoy/coq_jupyter/issues/21
        # https://github.com/EugeneLoy/coq_jupyter/issues/23

        result = self._execute_cell("Compute 5001.")

        self.assertIn("Warning: ", result)
        self.assertNotIn("<warning>", result)

    def test_coq_jupyter____when_executing_command_that_results_in_error____prints_error_once(self):
        result = self._execute_cell("Compute INVALID_REFERENCE.")

        self.assertEqual(result.count("Error: The reference INVALID_REFERENCE was not found"), 1, "result: " + repr(result))
        self.assertNotIn("<error>", result)

    def test_coq_jupyter____when_executing_command_that_results_in_notice_message____does_not_print_notice_message_level(self):
        (_, command) = self._build_sum_command()
        result = self._execute_cell(command)

        self.assertNotIn("notice", result.lower())

    def test_coq_jupyter____executing_code_with_unclosed_comment____prints_error(self):
        (_, command) = self._build_sum_command()
        result = self._execute_cell(command + " (* ")

        self.assertIn("Unterminated comment", result)

    def test_coq_jupyter____executing_code_surrounded_by_unclosed_comments____prints_evaluation_result(self):
        (expected_result, command) = self._build_sum_command()
        result = self._execute_cell("(* comment *)" + command + "(* comment *)")

        self.assertIn(expected_result, result)
        self.assertNotIn("error", result.lower())

    def test_coq_jupyter____executing_code_with_comments_woven_in____prints_evaluation_result(self):
        result = self._execute_cell("Check (* some comment with '.' in the middle *) I.")

        self.assertIn("True", result)
        self.assertNotIn("error", result.lower())

    def test_coq_jupyter____executing_code_comments_only____does_not_result_in_error(self):
        result = self._execute_cell("(* comment *)")

        self.assertNotIn("error", result.lower())

    def test_coq_jupyter____executing_code_with_non_xml_symbols____prints_evaluation_result(self):
        code = """
        Compute
        match 0 with
          | 0 => 1 + 1
          | S n' => n'
        end.
        """
        result = self._execute_cell(code)

        self.assertIn("2", result, msg="Code:\n{}".format(code))
        self.assertNotIn("error", result.lower(), msg="Code:\n{}".format(code))

    def test_coq_jupyter____executing_long_running_code_____prints_evaluation_result(self):
        code = "Goal True. timeout 10 (repeat eapply proj1)."
        result = self._execute_cell(code)

        self.assertIn("Tactic timeout", result)

    def test_coq_jupyter____executing_code_with_undotted_separators____prints_evaluation_result(self):
        fixture = [
            ("-", "-", ""),
            ("*", "*", ""),
            ("+", "+", ""),
            ("{", "{", "}"),
            ("1:{", "1 : {", "}"),
            ("[G1]:{", "[ g2_' ] : {", "}"),
            ("---", "---", "")
        ]
        for (opening_separator1, opening_separator2, closing_separator) in fixture:
            (expected_results, commands) = zip(*[self._build_sum_command() for _ in range(4)])
            code = """
            Goal True /\ True.
            split ; [ refine ?[G1] | refine ?[g2_'] ].
            {0} {3}
                {4}
              exact I.
            {2}
            {1} {5}
                {6}
              exact I.
            {2}
            Qed.
            """.format(opening_separator1, opening_separator2, closing_separator, *commands)

            result = self._execute_cell(code)

            for expected_result in expected_results:
                self.assertIn(expected_result, result, msg="Code:\n{}".format(code))
                self.assertNotIn("error", result.lower(), msg="Code:\n{}".format(code))



if __name__ == '__main__':
    unittest.main()
