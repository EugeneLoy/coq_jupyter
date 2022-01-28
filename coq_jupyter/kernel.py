from __future__ import unicode_literals

import sys
import traceback
import time

from traitlets import Unicode, Undefined
from uuid import uuid4
from ipykernel.kernelbase import Kernel
from .coqtop import Coqtop, CoqtopError
from .renderer import Renderer, HTML_ROLLED_BACK_STATUS_MESSAGE, TEXT_ROLLED_BACK_STATUS_MESSAGE


__version__ = '1.6.0'


CELL_COMM_TARGET_NAME = "coq_kernel.kernel_comm"


class CellRecord:

    def __init__(self, state_label_before, state_label_after, evaluated, rolled_back, execution_id, parent_header):
        self.state_label_after = state_label_after
        self.state_label_before = state_label_before
        self.evaluated = evaluated
        self.rolled_back = rolled_back
        self.execution_id = execution_id
        self.parent_header = parent_header

    def __repr__(self):
        return "<CellRecord: {}>".format(repr((self.state_label_before, self.state_label_after, self.evaluated, self.rolled_back, self.execution_id, self.parent_header)))


class CellJournal:

    def __init__(self, kernel):
        self.log = kernel.log # TODO
        self.history = []

    def add(self, state_label_before, state_label_after, evaluated, rolled_back, execution_id, parent_header):
        record = CellRecord(state_label_before, state_label_after, evaluated, rolled_back, execution_id, parent_header)
        self.history.append(record)
        return record

    def find_by_execution_id(self, execution_id):
        result = list(filter(lambda r: r.execution_id == execution_id, self.history))
        if len(result) == 1:
            return result[0]
        else:
            return None

    def find_rolled_back_transitively(self, state_label_before):
        return list(filter(lambda r: int(r.state_label_before) > int(state_label_before) and not r.rolled_back, self.history))


def shutdown_on_coqtop_error(function):
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except CoqtopError:
            self.log.exception("CoqtopError has occured. Scheduling shutdown.")
            from tornado import ioloop
            loop = ioloop.IOLoop.current()
            loop.add_timeout(time.time() + 0.1, loop.stop)
            raise

    return wrapper


class CoqKernel(Kernel):
    implementation = 'coq'
    implementation_version = __version__
    language = 'coq'

    @property
    def language_info(self):
        return {
            'name': 'coq',
            'mimetype': 'text/x-coq',
            'file_extension': '.v',
            'version': self.language_version
        }

    @property
    def banner(self):
        return self._coqtop.banner

    @property
    def language_version(self):
        return ".".join(map(str, self._coqtop.version))


    coqtop_executable = Unicode().tag(config=True)
    coqtop_args = Unicode().tag(config=True)


    @shutdown_on_coqtop_error
    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._coqtop = Coqtop(self, self.coqtop_executable, self.coqtop_args)
        self._journal = CellJournal(self)
        self._renderer = Renderer()
        self._kernel_comms = []
        for msg_type in ['comm_open', 'comm_msg', 'comm_close']:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            self.log.info("Processing 'execute_request', code: \n{}\n".format(repr(code)))

            if "coq_kernel_roll_back_cell" in self._parent_header["content"]:
                self._roll_back(self._parent_header["content"]["coq_kernel_roll_back_cell"])

            if code.strip("\n\r\t ") != "":
                state_label_before = self._coqtop.tip
                (evaluated, outputs) = shutdown_on_coqtop_error(lambda self: self._coqtop.eval(code))(self)
                state_label_after = self._coqtop.tip
                execution_id = self._parent_header["msg_id"]

                record = self._journal.add(state_label_before, state_label_after, evaluated, False, execution_id, self._parent_header)

                if not silent:
                    self.log.info("Sending 'execute_result', cell record:\n{}\n".format(repr(record)))
                    self._send_execute_result(outputs, execution_id, evaluated, False, state_label_after)

                return self._build_ok_content(state_label_before)
            else:
                self.log.info("code is empty - skipping evaluation and sending results.")
                return self._build_ok_content(self._coqtop.tip)

        except Exception as e:
            self.log.exception("Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(*sys.exc_info())

    def comm_open(self, stream, ident, msg):
        content = msg["content"]
        if content["target_name"] == CELL_COMM_TARGET_NAME:
            self._init_kernel_comm(content["comm_id"])
        else:
            self.log.error("Unexpected comm_open, msg: {}".format(repr(msg)))

    def comm_close(self, stream, ident, msg):
        self._kernel_comms.remove(msg["content"]["comm_id"])
        self.log.info("Kernel comm closed, msg: {}".format(repr(msg)))

    @shutdown_on_coqtop_error
    def comm_msg(self, stream, ident, msg):
        content = msg["content"]
        if content["comm_id"] in self._kernel_comms:
            if content["data"]["comm_msg_type"] == "roll_back":
                self._roll_back(msg["content"]["data"]["execution_id"])
            else:
                self.log.error("Unexpected comm_msg, msg: {}".format(repr(msg)))
        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}, opened comms: {}".format(repr(msg)), repr(self._kernel_comms))

    def _init_kernel_comm(self, comm_id):
        self._send_kernel_comm_opened_comm_msg(comm_id, self._journal.history)
        self._kernel_comms.append(comm_id)
        self.log.info("Kernel comm opened, comm_id: {}".format(comm_id))

    def _roll_back(self, execution_id):
        self.log.info("roll back, execution_id: {}".format(execution_id))
        cell_record = self._journal.find_by_execution_id(execution_id)

        if cell_record is not None and cell_record.evaluated and not cell_record.rolled_back:
            self._coqtop.roll_back_to(cell_record.state_label_before)

            for record in [cell_record] + self._journal.find_rolled_back_transitively(cell_record.state_label_before):
                # mark cell as rolled back
                record.rolled_back= True

                # update content of rolled back cell
                self._send_roll_back_update_display_data(record.parent_header, record.execution_id, record.evaluated, record.rolled_back)

                # update cell state via kernel comms
                for comm_id in self._kernel_comms:
                    self._send_cell_state_comm_msg(comm_id, record.execution_id, record.evaluated, record.rolled_back)

        else:
            self.log.info("Unexpected (possibly leftover) roll back request for execution_id: {}".format(execution_id))

    def _build_ok_content(self, state_label_before):
        return {
            'status': 'ok',
            'execution_count': int(state_label_before),
            'payload': [],
            'user_expressions': {},
        }

    def _build_error_content(self, ex_type, ex, tb):
        return {
            'status': 'error',
            'ename' : ex_type.__name__,
            'evalue' : repr(ex),
            'traceback' : traceback.format_list(traceback.extract_tb(tb))
        }

    def _build_display_data_content(self, text, html, execution_id, evaluated, rolled_back):
        return {
            'data': {
                'text/plain': text,
                'text/html': html
            },
            'metadata': {
                'coq_kernel_execution_id': execution_id,
                'coq_kernel_evaluated': evaluated,
                'coq_kernel_rolled_back': rolled_back
             },
            'transient': { 'display_id': execution_id }
        }

    def _send_kernel_comm_opened_comm_msg(self, comm_id, history):
        content = {
            "comm_id": comm_id,
            "data": {
                "comm_msg_type": "kernel_comm_opened",
                "history": [
                    {
                        "execution_id": record.execution_id,
                        "evaluated": record.evaluated,
                        "rolled_back": record.rolled_back
                    }
                    for record in history
                ]
            }
        }
        self.session.send(self.iopub_socket, "comm_msg", content, None, None, None, None, None, None)

    def _send_cell_state_comm_msg(self, comm_id, execution_id, evaluated, rolled_back):
        content = {
            "comm_id": comm_id,
            "data": {
                "comm_msg_type": "cell_state",
                "execution_id": execution_id,
                "evaluated": evaluated,
                "rolled_back": rolled_back
            }
        }
        self.session.send(self.iopub_socket, "comm_msg", content, None, None, None, None, None, None)

    def _send_roll_back_update_display_data(self, parent_header, execution_id, evaluated, rolled_back):
        content = self._build_display_data_content(TEXT_ROLLED_BACK_STATUS_MESSAGE, HTML_ROLLED_BACK_STATUS_MESSAGE, execution_id, evaluated, rolled_back)
        self.session.send(self.iopub_socket, "update_display_data", content, parent_header, None, None, None, None, None)

    def _send_execute_result(self, outputs, execution_id, evaluated, rolled_back, state_label_after):
        text = self._renderer.render_text_result(outputs)
        html = self._renderer.render_html_result(outputs, execution_id, evaluated)
        content = self._build_display_data_content(text, html, execution_id, evaluated, rolled_back)
        content['execution_count'] = int(state_label_after)
        self.send_response(self.iopub_socket, 'execute_result', content)
