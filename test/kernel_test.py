import unittest
import jupyter_kernel_test

class KernelTests(jupyter_kernel_test.KernelTests):

    # Required by jupyter_kernel_test.KernelTests:
    kernel_name = "coq"
    language_name = "coq"

    def _build_sum_command(self, lhs, rhs):
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
        (expected_result, command) = self._build_sum_command(100, 1)
        result = self._execute_cell(command)
        self.assertIn(expected_result, result)

    def test_coq_jupyter____executing_one_command____does_not_print_command(self):
        (expected_result, command) = self._build_sum_command(100, 2)
        result = self._execute_cell(command)
        self.assertNotIn(command, result)

    def test_coq_jupyter____executing_one_command____does_not_print_hidden_checkpoint_command_and_its_result(self):
        result = self._execute_cell("Check True.")
        hidden_checkpoint_command_part = "Compute"
        hidden_checkpoint_command_result_part = "nat"
        self.assertNotIn(hidden_checkpoint_command_part, result)
        self.assertNotIn(hidden_checkpoint_command_result_part, result)

    def test_coq_jupyter____executing_compute_command_when_not_proving____does_not_print_proving_context(self):
        (expected_result, command) = self._build_sum_command(100, 3)
        result = self._execute_cell(command)
        self.assertNotIn("proving:", result)
        self.assertNotIn("subgoal", result)

    def test_coq_jupyter____executing_multiple_commands____prints_computed_command_results(self):
        (expected_result1, command1) = self._build_sum_command(100, 4)
        (expected_result2, command2) = self._build_sum_command(100, 5)
        result = self._execute_cell(command1 + " " + command2)
        self.assertIn(expected_result1, result)
        self.assertIn(expected_result2, result)

    def test_coq_jupyter____executing_commands_when_proving____prints_proving_context(self):
        result = self._execute_cell("Theorem t1 : True.")
        self.assertIn("1 subgoal", result)
        self.assertIn("proving: t1", result)

        result = self._execute_cell(self._build_sum_command(100, 6)[1])
        self.assertIn("1 subgoal", result)
        self.assertIn("proving: t1", result)

        result = self._execute_cell("Proof. pose (i1 := I).")
        self.assertIn("1 subgoal", result)
        self.assertIn("i1 := I : True", result)
        self.assertIn("proving: t1", result)

        result = self._execute_cell(self._build_sum_command(100, 7)[1])
        self.assertIn("1 subgoal", result)
        self.assertIn("i1 := I : True", result)
        self.assertIn("proving: t1", result)

        result = self._execute_cell("exact i1. Qed.")
        self.assertNotIn("1 subgoal", result)
        self.assertNotIn("No more subgoals", result)
        self.assertNotIn("i1 := I : True", result)
        self.assertNotIn("proving:", result)

        result = self._execute_cell(self._build_sum_command(100, 8)[1])
        self.assertNotIn("1 subgoal", result)
        self.assertNotIn("No more subgoals", result)
        self.assertNotIn("i1 := I : True", result)
        self.assertNotIn("proving:", result)

    def test_coq_jupyter____when_proving____does_not_print_hidden_commands_and_their_results(self):
        result = self._execute_cell("Theorem t2 : True.")

        hidden_checkpoint_command_part = "Compute"
        hidden_checkpoint_command_result_part = "nat"
        hidden_show_command = "Show."

        self.assertNotIn(hidden_checkpoint_command_part, result)
        self.assertNotIn(hidden_checkpoint_command_result_part, result)
        self.assertNotIn(hidden_show_command, result)
        # Note: the result of Show command actually should be shown, so there is no need to verify its absense

        self._execute_cell("Proof. exact I. Qed.") # TODO move cleanup to teardown

    def test_coq_jupyter____when_proving____prints_most_recent_proving_context_once(self):
        result = self._execute_cell("Theorem t3 : bool. Proof. pose (b1 := true). pose (b2 := false).")
        self.assertEqual(result.count("proving: t3"), 1, "result: " + repr(result))
        self.assertEqual(result.count("1 subgoal"), 1, "result: " + repr(result))
        self.assertEqual(result.count("No more subgoals"), 0, "result: " + repr(result))
        self.assertEqual(result.count("b1 := true : bool"), 1, "result: " + repr(result))
        self.assertEqual(result.count("b2 := false : bool"), 1, "result: " + repr(result))

        result = self._execute_cell("exact b2.")
        self.assertEqual(result.count("proving: t3"), 1, "result: " + repr(result))
        self.assertEqual(result.count("1 subgoal"), 0, "result: " + repr(result))
        self.assertEqual(result.count("No more subgoals"), 1, "result: " + repr(result))
        self.assertEqual(result.count("b1 := true : bool"), 0, "result: " + repr(result))
        self.assertEqual(result.count("b2 := false : bool"), 0, "result: " + repr(result))

        self._execute_cell("Qed.") # TODO move cleanup to teardown

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
                # missing "." in last command may cause hidden command to appear in error message.
                # In this case alternative footer explaining error should be shown instead of coqtop error output
                "Syntax error: '.' expected after" if t != 3 else "Cell evaluation error: last cell command is incomplete or malformed."
            )
            for t in (1,2,3)
        ]
        fixture = cases_with_reference_error + cases_with_syntax_error + cases_with_incomplete_command_error

        for f in range(len(fixture)):
            (invalid_definition, valid_definitions, commited_definition, code, expected_error_message) = fixture[f]

            self._execute_cell(commited_definition[1])

            result = self._execute_cell(code)
            self.assertIn("cell rolled back", result.lower(), "fixture: {}".format(repr(fixture[f])))
            self.assertIn(expected_error_message, result, "fixture: {}".format(repr(fixture[f])))

            # verify rollback
            result = self._execute_cell("Print All.")
            self.assertIn(commited_definition[0], result, "fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(invalid_definition, result, "fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(valid_definitions[0], result, "fixture: {}".format(repr(fixture[f])))
            self.assertNotIn(valid_definitions[1], result, "fixture: {}".format(repr(fixture[f])))

    def test_coq_jupyter____when_executing_command_that_results_in_warning____prints_warning(self):
        # this test ensures fix of the following:
        # https://github.com/EugeneLoy/coq_jupyter/issues/21
        # https://github.com/EugeneLoy/coq_jupyter/issues/23

        result = self._execute_cell("Compute 5001.")

        self.assertIn("Warning: ", result)
        self.assertNotIn("<warning>", result)


if __name__ == '__main__':
    unittest.main()
