import os

class ExtraPin:
    def __init__(self, config):
        printer = config.get_printer()
        self.gcode = printer.lookup_object('gcode')
        self.ppin = printer.lookup_object('pins')
        self.name = config.get_name().split()[1]
        self.board = config.get('board')
        self.pin = config.get('pin')
        self.start_value = config.getboolean('start_value', False)
        self.poweroff_value = config.getboolean('poweroff_value', False)
        self.last_value = not self.start_value
        self.dict_pins = {0:['PL10', '8'], 1:['PL02','3'], 2:['PL03','4'], 3:['PD18','6'], 4:['PD15','9'], 5:['PD16','10'], 6:['PD21','13'], 7:['PL08','16']}
        
        printer.register_event_handler('klippy:ready', self._handle_ready_klippy)
    
    def _handle_ready_klippy(self):
        if self.board == 'control_board':
            self.mcu_pin = self.ppin.setup_pin('digital_out', self.pin)
            self.mcu_pin.setup_max_duration(0)
            self.mcu_pin.setup_start_value(self.start_value, self.poweroff_value)
            self.gcode.register_mux_command("TOGGLE", "DEVICE", self.name, self.cmd_toggleDevice)
        elif self.board == 'single_board_computer':
            os.system('cd /${HOME}')
            self.sbc_pin = self._get_pin_number(self.pin)
            os.system('gpio mode ' + str(self.sbc_pin) + ' out') # check it!!!!!!!!
    
        self.gcode.register_mux_command("EXTRA_PIN_INFO", "BUTTON", self.name, self.cmd_getInfo)
        
    def get_status(self, eventtime):
        if self.board == 'control_board':
            return {'board':    'control_board',
                    'cmd':      'TOGGLE DEVICE=' + str(self.name)
                    }
        elif self.board == 'single_board_computer':
            return {'board':    'single_board_computer',
                    'cmd':      'gpio write ' + str(self.sbc_pin) + ' ',
                    'stat':     0
                    } # what cmd use?
    def cmd_getInfo(self, gcmd):
        response = ("board: " + str(self.board) + '\n' +
                    "start_value: " + str(self.start_value) + '\n' +
                    "poweroff_value: " + str(self.poweroff_value) + '\n'+
                    "pin: " + str(self.pin) + '\n' + 
                    "last value: " + str(self.last_value))
        gcmd.respond_info(response)

    def cmd_toggleDevice(self, gcmd):
        response = ("value: " + str(self.last_value))
        gcmd.respond_info(response)
        self.last_value = self._update_digital(self.last_value)
        
        

    def _update_digital(self, value):
        self.mcu_pin.update_digital(value)
        return not value

    def _get_pin_number(self, pin):
        for i in list(self.dict_pins):
            if pin == self.dict_pins[i][0]:
                return self.dict_pins[i][1]







def load_config_prefix(config):
    return ExtraPin(config)
