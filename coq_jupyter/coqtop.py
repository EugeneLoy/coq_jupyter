from __future__ import unicode_literals

import pexpect
import re
import random
import sys

from operator import itemgetter


PROMPT = "\<prompt\>.+?\s\<\s(?P<state_label>\d+)\s\|(?P<proving>.*?)\|\s\d+\s\<\s\<\/prompt\>"

ANSI_ESCAPE_PATTERN = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]') # see: https://stackoverflow.com/a/38662876/576549

class CoqtopWrapper:

    def __init__(self, kernel, coqtop_args):
        self.log = kernel.log # TODO
        self._coqtop = pexpect.spawn("coqtop -emacs -quiet {}".format(coqtop_args), echo=False, encoding="utf-8", codec_errors="replace")
        self._state_label = "1"
        self.eval("(* dummy init command *)")

    def eval(self, code):
        state_label_before = self._state_label
        checkpoint_marker_lhs = random.randint(0, 499)
        checkpoint_marker_rhs = random.randint(0, 499)
        checkpoint_marker = str(checkpoint_marker_lhs + checkpoint_marker_rhs)
        eval_checkpoint_command = "Compute {} + {}.".format(checkpoint_marker_lhs, checkpoint_marker_rhs)
        hidden_commands_issued = 1

        # attempt evaluation
        self._coqtop.send("{}\n{}\n".format(code, eval_checkpoint_command))

        # collect evaluation output
        outputs = []
        while True:
            (prompt_match, raw_output, simplified_output, error_message) = self._expect_coqtop_prompt()
            outputs.append((prompt_match, raw_output, simplified_output, error_message))

            if checkpoint_marker in simplified_output:
                self.log.debug("checkpoint reached")
                break

            if error_message and eval_checkpoint_command in simplified_output:
                self.log.debug("checkpoint eval failed")
                break

        # query proof state if proving something now
        if outputs[-1][0].group("proving") != "":
            self._coqtop.sendline("Show.")
            outputs.append(self._expect_coqtop_prompt())
            hidden_commands_issued += 1

        # do full cell rollback if error were detected
        if any(map(itemgetter(3), outputs)):
            self._coqtop.sendline("BackTo {}.".format(state_label_before))
            self._expect_coqtop_prompt()

            raw_outputs = []
            footer_message = "Cell evaluation error: some of the commands resulted in error. Cell rolled back."
            for (_, raw_output, simplified_output, _) in outputs:
                if eval_checkpoint_command in simplified_output:
                    footer_message = "Cell evaluation error: last cell command is incomplete or malformed. Cell rolled back."
                    break

                if checkpoint_marker in simplified_output:
                    break

                raw_outputs.append(simplified_output)

            return (raw_outputs, footer_message, True, state_label_before, state_label_before)

        # rollback issued hidden commands
        # TODO not 100% sure if this rollback is really needed. Leave it for now.
        self._coqtop.sendline("BackTo {}.".format(outputs[-hidden_commands_issued][0].group("state_label")))
        self._expect_coqtop_prompt()

        # treat state after hidden commands rollback as 'commited'
        self._state_label = self._coqtop.match.group("state_label")

        # build cell output message
        raw_outputs = list(map(itemgetter(1), outputs))
        del raw_outputs[-hidden_commands_issued] # omit checkpoint marker output

        if self._coqtop.match.group("proving") != "":
            footer_message = "Cell evaluated, proving: {}.".format(self._coqtop.match.group("proving"))
        else:
            footer_message = "Cell evaluated."

        return (raw_outputs, footer_message, False, state_label_before, self._state_label)

    def _expect_coqtop_prompt(self):
        self.log.debug("expecting coqtop prompt")
        self._coqtop.expect(PROMPT, None)

        prompt_match = self._coqtop.match
        self.log.debug("coqtop prompt: {}".format(repr(prompt_match)))

        raw_output = self._coqtop.before
        self.log.debug("coqtop output (raw): {}".format(repr(raw_output)))

        simplified_output = self._simplify_output(raw_output)
        self.log.debug("coqtop output (simplified): {}".format(repr(simplified_output)))

        error_message = self._is_error_output(simplified_output)
        self.log.debug("coqtop output contains error message: {}".format(error_message))

        return (prompt_match, raw_output, simplified_output, error_message)

    def _simplify_output(self, output):
        # clean colors
        output = ANSI_ESCAPE_PATTERN.sub("", output)
        # replace \n\r with \n
        output = "\n".join(output.splitlines())
        return output.strip("\n\t ")

    def _is_error_output(self, output):
        lines = output.splitlines()

        if len(lines) == 0:
            return False

        error_location_found = False
        for line in lines:
            error_location_found = error_location_found or line.startswith("Toplevel input, characters")
            if error_location_found and (line.startswith("Error:") or line.startswith("Syntax error:")):
                return True

        return False
