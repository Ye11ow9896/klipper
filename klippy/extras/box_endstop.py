

class BoxEndstop:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.pin = config.get('pin')
        self.last_state = 0
        buttons = self.printer.load_object(config, "buttons")
        buttons.register_buttons([self.pin], self.button_callback)
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command("BOX_ENDSTOP_STAT", self.cmd_boxEndstopStat)

    def cmd_boxEndstopStat(self, gcmd):
        gcmd.respond_info(str(self.get_status()['state']))

    def button_callback(self, eventtime, state):
        self.last_state = state

    def get_status(self, eventtime=None):
        return {'state': self.last_state}

def load_config(config):
    return BoxEndstop(config)
