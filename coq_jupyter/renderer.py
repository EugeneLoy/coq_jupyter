from __future__ import unicode_literals

import os


HTML_SUCCESS_STATUS_MESSAGE = """
<div class="coq_kernel_rich_cell_output coq_kernel_status_message_area">
    <i class="fa-check fa text-success"></i>
    <span>Cell evaluated.</span>
</div>
"""

HTML_ERROR_STATUS_MESSAGE = """
<div class="coq_kernel_rich_cell_output coq_kernel_status_message_area">
    <i class="fa-times fa text-danger"></i>
    <span>Error while evaluating cell. Cell rolled back.</span>
</div>
"""

HTML_ROLLED_BACK_STATUS_MESSAGE = """
<div class="coq_kernel_rich_cell_output coq_kernel_status_message_area coq_kernel_rolled_back_status_message">
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLLED_BACK_STATUS_MESSAGE_HIDDEN = """
<div class="coq_kernel_rich_cell_output coq_kernel_status_message_area coq_kernel_rolled_back_status_message" style="display: none">
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

TEXT_ROLLED_BACK_STATUS_MESSAGE = "Cell rolled back."

HTML_OUTPUT_TEMPLATE = """
<div class="coq_kernel_output_area">
    <pre>{0}</pre>
</div>
"""

HTML_ROLL_BACK_CONTROLS = """
<div class="coq_kernel_rich_cell_output coq_kernel_roll_back_controls_area" style="display: none; position: relative;">
    <button class="btn btn-default btn-xs coq_kernel_roll_back_button" style="margin-top: 5px;" onclick="CoqKernel.roll_back(this)">
        <i class="fa-step-backward fa"></i>
        <span class="toolbar-btn-label">Rollback cell</span>
    </button>

    <div style="display: inline-block; vertical-align: middle; margin-top: 5px; padding-left: 0; padding-right: 0;">
      <input class="coq_kernel_auto_roll_back_checkbox" type="checkbox" value="" onchange="CoqKernel.toggle_auto_roll_back(this)" checked>
      <label">Auto rollback</label>
    </div>
</div>
"""


class Renderer:

    def render_text_result(self, outputs):
        cell_output = "\n\n".join(outputs)
        return cell_output

    def render_html_result(self, outputs, execution_id, success_output):
        html = HTML_OUTPUT_TEMPLATE.format(self.render_text_result(outputs))
        if success_output:
            html += HTML_SUCCESS_STATUS_MESSAGE
            html += HTML_ROLLED_BACK_STATUS_MESSAGE_HIDDEN
            html += HTML_ROLL_BACK_CONTROLS
        else:
            html += HTML_ERROR_STATUS_MESSAGE

        return html
