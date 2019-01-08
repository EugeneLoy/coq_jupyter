
function CoqKernelRollbackComm(display_id) {
    var self = this;
    self.display_id = display_id;
    self.button_id = "#rollblack_button_" + self.display_id;
    self.rollback_message_id = "#rollback_message_" + self.display_id;
    self.output_id = "#output_" + self.display_id;

    self.jupyter = require('base/js/namespace');

    self.init = function () {
        if (self.jupyter.notebook.kernel !== null) {
            console.info('Initializing rollback comm for: ' + self.display_id);
            self.comm = self.jupyter.notebook.kernel.comm_manager.new_comm('coq_kernel.rollback_comm', { 'display_id': self.display_id });
            self.comm.on_msg(self.handle_comm_message);
            self.comm.send({ 'comm_msg_type': 'request_rollback_sate' });
        } else {
            // kernel is not ready yet - try later
            setTimeout(self.init, 100)
        }
    };

    self.rollback = function () {
        self.comm.send({ 'comm_msg_type': 'rollback' });
        $(self.button_id).prop('disabled', true);
    };

    self.handle_comm_message = function(msg) {
        if (msg.content.data.comm_msg_type === "rollback_state") {
            $(self.output_id).toggle(!msg.content.data.rolled_back)
            $(self.button_id).toggle(!msg.content.data.rolled_back)
            $(self.rollback_message_id).toggle(msg.content.data.rolled_back)
        } else {
            console.error('Unexpected comm message: ' + JSON.stringify(msg));
        }
    }
};
