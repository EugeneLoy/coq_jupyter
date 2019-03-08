from __future__ import unicode_literals

import os

HTML_OUTPUT_TEMPLATE = """
<div class="coq_kernel_output_area_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-check fa text-success"></i>
    <span>Cell evaluated.</span>
</div>
"""

HTML_ERROR_OUTPUT_TEMPLATE = """
<div class="coq_kernel_output_area_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-times fa text-danger"></i>
    <span>Error while evaluating cell. Cell rolled back.</span>
</div>
"""

HTML_ROLL_BACK_MESSAGE_TEMPLATE = """
<div class="coq_kernel_roll_back_message_{0}" style="display: none">
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLL_BACK_MESSAGE = """
<div>
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

TEXT_ROLL_BACK_MESSAGE = "Cell rolled back."

HTML_ROLL_BACK_BUTTON_TEMPLATE = """
<div class="coq_kernel_roll_back_button_area_{0} coq_kernel_roll_back_button_area" style="display: none; position: relative;">
    <button class="btn btn-default btn-xs coq_kernel_roll_back_button" style="margin-top: 5px;" onclick="CoqKernel.roll_back(this)">
        <i class="fa-step-backward fa"></i>
        <span class="toolbar-btn-label">Rollback cell</span>
    </button>
</div>
"""


class Renderer:

    def render_text_result(self, outputs):
        cell_output = "\n\n".join(outputs)
        return cell_output

    def render_html_result(self, outputs, execution_id, success_output):
        if success_output:
            html = HTML_OUTPUT_TEMPLATE.format(execution_id, self.render_text_result(outputs))
            html += HTML_ROLL_BACK_MESSAGE_TEMPLATE.format(execution_id)
            html += HTML_ROLL_BACK_BUTTON_TEMPLATE.format(execution_id)
        else:
            html = HTML_ERROR_OUTPUT_TEMPLATE.format(execution_id, self.render_text_result(outputs))

        return html
