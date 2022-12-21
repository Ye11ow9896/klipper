SAFE_BOX_TEMP = 70

class BoxEndstop:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.pin = config.get('endstop_pin')
        self.last_state = 0
        buttons = self.printer.load_object(config, "buttons")
        buttons.register_buttons([self.pin], self._button_callback)

    def _button_callback(self, eventtime, state):
        self.last_state = state

    def get_status(self, eventtime=None):
        return {'state': self.last_state}

class SignalServo:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object('pins')

        # get signal values
        self.period = config.getfloat('period')
        self.close_pulse = config.getfloat('close_pulse')
        self.open_pulse = config.getfloat('open_pulse')

        # init PWM. 
        self.sig =  ppins.setup_pin('pwm', config.get('pin'))
        self.sig.setup_max_duration(0.)
        self.sig.setup_cycle_time(self.period)
        self.duty_cycle = (1./self.period) * self.open_pulse
        self.sig.setup_start_value(1 - self.duty_cycle, 0.)
    
    def open_door(self):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.duty_cycle = (1./self.period) * self.open_pulse
        self.sig.set_pwm(print_time, 1 - self.duty_cycle)

    def close_door(self):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.duty_cycle = (1./self.period) * self.close_pulse
        self.sig.set_pwm(print_time, 1 - self.duty_cycle)
    

class DoorControl:
    def __init__(self, config):
        self.endstop = BoxEndstop(config)
        self.signal = SignalServo(config)
        self.printer = config.get_printer()
        self.pheaters = self.printer.load_object(config, 'heaters')
        self.reactor = self.printer.get_reactor()

        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('TEST', self.cmd_TEST)

        self.printer.register_event_handler('klippy:ready', self._handle_ready_klippy)

    def cmd_TEST(self, gcmd):
        res = (" ")
        if self._endstop_status():
            res += ("end status worked!" + '\n')
            if self.heater_box.get_temp(0)[0] >= SAFE_BOX_TEMP:    
                res += ("CLOSE" + '\n')
            else:
                res += ("OPEN" + '\n')
        res += (str(self._endstop_status()) + '\n')
        res += (str(self.heater_box.get_temp(0)[0]))
        gcmd.respond_info(res)

    def _handle_ready_klippy(self):
        self.heater_box = self.pheaters.lookup_heater('heater_box')
        # we need to check door endstop and temperature box sensor every second 
        check_sensors_timer = self.reactor.register_timer(self._check_sensors, self.reactor.monotonic() + .5)

    def _endstop_status(self):
        return bool(self.endstop.get_status()['state'])

    def _check_sensors(self, eventtime):
        if self._endstop_status():
            if self.heater_box.get_temp(0)[0] >= SAFE_BOX_TEMP:    
                self.signal.close_door()
            else:
                self.signal.open_door()
        return eventtime + .5
    
def load_config(config):
    return DoorControl(config)