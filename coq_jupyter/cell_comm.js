
function CoqKernelCellComm(display_id) {
    var self = this;
    self.display_id = display_id;
    self.roll_back_button_id = "#rollblack_button_" + self.display_id;
    self.roll_back_message_id = "#roll_back_message_" + self.display_id;
    self.output_id = "#output_" + self.display_id;

    self.jupyter = require('base/js/namespace');

    self.init = function () {
        if (self.jupyter.notebook.kernel !== null) {
            console.info('Initializing cell comm for: ' + self.display_id);
            self.comm = self.jupyter.notebook.kernel.comm_manager.new_comm('coq_kernel.cell_comm', { 'display_id': self.display_id });
            self.comm.on_msg(self.handle_comm_message);
            self.comm.send({ 'comm_msg_type': 'request_cell_sate' });
        } else {
            // kernel is not ready yet - try later
            setTimeout(self.init, 100)
        }
    };

    self.roll_back = function () {
        self.comm.send({ 'comm_msg_type': 'roll_back' });
        $(self.roll_back_button_id).prop('disabled', true);
        $(self.roll_back_button_id).removeClass("enabled_roll_back_button");
    };

    self.handle_comm_message = function(msg) {
        if (msg.content.data.comm_msg_type === "cell_state") {
            $(self.output_id).toggle(!msg.content.data.rolled_back);
            $(self.roll_back_message_id).toggle(msg.content.data.rolled_back);
            $(self.roll_back_button_id).toggle(msg.content.data.evaluated && !msg.content.data.rolled_back);
            if (msg.content.data.evaluated && !msg.content.data.rolled_back) {
                $(self.roll_back_button_id).addClass("enabled_roll_back_button");
            } else {
                $(self.roll_back_button_id).removeClass("enabled_roll_back_button");
            }
        } else {
            console.error('Unexpected comm message: ' + JSON.stringify(msg));
        }
    }
};
