from __future__ import unicode_literals

import os

HTML_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-check fa text-success"></i>
    <span>{2}</span>
</div>
"""

HTML_ERROR_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-times fa text-danger"></i>
    <span>{2}</span>
</div>
"""

HTML_ROLLBACK_MESSAGE_TEMPLATE = """
<div id="rollback_message_{0}" style="display: none">
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLLBACK_MESSAGE = """
<div>
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLLBACK_BUTTON_TEMPLATE = """
<div style="position: relative;">
    <button id="rollblack_button_{0}" class="btn btn-default btn-xs" style="display: none; margin-top: 5px;" onclick="coq_kernel_rollback_comm_{0}.rollback()">
        <i class="fa-step-backward fa"></i>
        <span class="toolbar-btn-label">Rollback cell</span>
    </button>
</div>
"""

HTML_ROLLBACK_COMM_INIT_TEMPLATE = """
<script>
    var coq_kernel_rollback_comm_{0} = new CoqKernelRollbackComm('{0}');
    coq_kernel_rollback_comm_{0}.init();
</script>
"""

with open(os.path.join(os.path.dirname(__file__), "rollback_comm.js"), 'r') as f:
    HTML_ROLLBACK_COMM_DEFINITION = """<script>{}</script>""".format(f.read())

class Renderer:

    def render_text_result(self, raw_outputs, footer_message):
        cell_output = "\n".join(raw_outputs)

        # strip extra tag formating
        # TODO this is a temporary solution that won't be relevant after implementing ide xml protocol
        for tag in ["warning", "infomsg"]:
            cell_output = cell_output.replace("<{}>".format(tag), "").replace("</{}>".format(tag), "")

        cell_output = cell_output.replace("(dependent evars: (printing disabled) )", "")

        cell_output = cell_output.rstrip("\n\r\t ").lstrip("\n\r")

        if footer_message is not None:
            cell_output += "\n\n" + footer_message

        return cell_output

    def render_html_result(self, raw_outputs, footer_message, display_id, success_output):
        if success_output:
            html = HTML_OUTPUT_TEMPLATE.format(display_id, self.render_text_result(raw_outputs, None), footer_message)
            html += HTML_ROLLBACK_MESSAGE_TEMPLATE.format(display_id)
            html += HTML_ROLLBACK_BUTTON_TEMPLATE.format(display_id)
            html += HTML_ROLLBACK_COMM_DEFINITION
            html += HTML_ROLLBACK_COMM_INIT_TEMPLATE.format(display_id)
        else:
            html = HTML_ERROR_OUTPUT_TEMPLATE.format(display_id, self.render_text_result(raw_outputs, None), footer_message)

        return html
