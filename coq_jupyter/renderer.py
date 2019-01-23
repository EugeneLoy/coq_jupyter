from __future__ import unicode_literals

import os

HTML_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-check fa text-success"></i>
    <span>Cell evaluated.</span>
</div>
"""

HTML_ERROR_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-times fa text-danger"></i>
    <span>Error while evaluating cell. Cell rolled back.</span>
</div>
"""

HTML_ROLL_BACK_MESSAGE_TEMPLATE = """
<div id="roll_back_message_{0}" style="display: none">
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
<div style="position: relative;">
    <button id="rollblack_button_{0}" class="btn btn-default btn-xs" style="display: none; margin-top: 5px;" onclick="coq_kernel_cell_comm_{0}.roll_back()">
        <i class="fa-step-backward fa"></i>
        <span class="toolbar-btn-label">Rollback cell</span>
    </button>
</div>
"""

HTML_CELL_COMM_INIT_TEMPLATE = """
<script>
    var coq_kernel_cell_comm_{0} = new CoqKernelCellComm('{0}');
    coq_kernel_cell_comm_{0}.init();
</script>
"""

with open(os.path.join(os.path.dirname(__file__), "cell_comm.js"), 'r') as f:
    HTML_CELL_COMM_DEFINITION = """<script>{}</script>""".format(f.read())

class Renderer:

    def render_text_result(self, outputs):
        cell_output = "\n\n".join(outputs)
        return cell_output

    def render_html_result(self, outputs, display_id, success_output):
        if success_output:
            html = HTML_OUTPUT_TEMPLATE.format(display_id, self.render_text_result(outputs))
            html += HTML_ROLL_BACK_MESSAGE_TEMPLATE.format(display_id)
            html += HTML_ROLL_BACK_BUTTON_TEMPLATE.format(display_id)
            html += HTML_CELL_COMM_DEFINITION
            html += HTML_CELL_COMM_INIT_TEMPLATE.format(display_id)
        else:
            html = HTML_ERROR_OUTPUT_TEMPLATE.format(display_id, self.render_text_result(outputs))

        return html
