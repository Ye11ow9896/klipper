from heaters import Heater

ON = 1
OFF = 0

class SetupPin(Heater):
    def __init__(self, config, pin_name):
        ppins = config.get_printer().lookup_object('pins')
        self.start_value = bool(0)
        self.poweroff_value = bool(0)
        self.max_duration = 0
        self.pin = config.get(pin_name)
        self.pin_obj = self.pin
        self.pin_obj = ppins.setup_pin('digital_out', self.pin)
        self.pin_obj.setup_max_duration(self.max_duration)
        self.pin_obj.setup_start_value(self.start_value, self.poweroff_value)
    
    def update_digital(self, value):
        self.pin_obj.update_digital(value)
        self.start_value = value


class LEDsStatus:
    def __init__(self, config):

        self.printer = config.get_printer()
        self.pheaters = self.printer.load_object(config, 'heaters')
        self.all_heaters = self.pheaters.get_all_heaters() 
        gcode = self.printer.lookup_object('gcode')

        # create objects for leds managment
        self.leds = {}
        self.leds['heater_box'] = SetupPin(config, 'box_pin')
        self.leds['heater_bed'] = SetupPin(config, 'bed_pin')
        self.leds['extruder'] = SetupPin(config, 'extr1_pin')
        self.leds['extruder1'] = SetupPin(config, 'extr2_pin')
        self.leds['print_stat'] = SetupPin(config, 'print_stat_pin')
        self.leds['error_stat'] = SetupPin(config, 'error_stat_pin')
        self.leds['ready_stat'] = SetupPin(config, 'ready_stat_pin')

        # Register event hundler for RGB LCD
        self.printer.register_event_handler('klippy:ready', self._handle_ready_klippy)
        self.printer.register_event_handler('print_stats:printing', self._handle_printing)
        self.printer.register_event_handler('print_stats:error', self._handle_error)
        self.printer.register_event_handler('print_stats:cancelled', self._handle_cancelled)
        self.printer.register_event_handler('print_stats:paused', self._handle_paused)
        self.printer.register_event_handler('print_stats:complete', self._handle_complete)

        # Register command for check pins
        gcode.register_command("CHECK_SETUP_PIN", self.cmd_checkPins)

        # Register command for set pins
        gcode.register_command("SETPIN_BOX", self.cmd_setPin_box)

    def _handle_ready_klippy(self):
        self._set_ready_led()
        reactor = self.printer.get_reactor()
        reactor.register_timer(self._check_heaters, reactor.monotonic()+0.1)

    def _handle_printing(self):
        self._set_print_led()

    def _handle_error(self):
        self._set_error_led()

    def _handle_cancelled(self):
        self._set_ready_led()

    def _handle_paused(self):
        self._set_ready_led()

    def _handle_complete(self):
        self._set_print_led()


    def cmd_checkPins(self, gcmd):
        for heater_name in self.all_heaters:
            if heater_name == 'heater_generic heater_box':
                heater_name = 'heater_box'
            self.heater = self.pheaters.lookup_heater(heater_name)
            #self.pwm = self.heater.get_pwm_status()
            self.target_temp = self.heater.get_target_temp()
            
            response = (str(self.target_temp) + "'\n'") 
            gcmd.respond_info(response)

    def cmd_setPin_box(self, gcmd):
        response = ("set pin value = " + str(self.leds['box'].start_value))
        self.leds['box'].update_digital(self.leds['box'].start_value)
        self.leds['box'].start_value = not self.leds['box'].start_value
        gcmd.respond_info(response)

    def _check_heaters(self, eventtime):
        for heater_name in self.all_heaters:
            if heater_name == 'heater_generic heater_box':
                heater_name = 'heater_box'
            self.heater = self.pheaters.lookup_heater(heater_name)
            self.target_temp = self.heater.get_target_temp()
            if self.target_temp > 0:
                self.leds[heater_name].update_digital(ON)
            else:
                self.leds[heater_name].update_digital(OFF)

        return eventtime + 0.1
       
    def _set_print_led(self):
        self.leds['print_stat'].update_digital(ON)
        self.leds['error_stat'].update_digital(OFF)
        self.leds['ready_stat'].update_digital(OFF)

    def _set_error_led(self):
        self.leds['print_stat'].update_digital(OFF)
        self.leds['error_stat'].update_digital(ON)
        self.leds['ready_stat'].update_digital(OFF)

    def _set_ready_led(self):
        self.leds['print_stat'].update_digital(OFF)
        self.leds['error_stat'].update_digital(OFF)
        self.leds['ready_stat'].update_digital(ON)

def load_config(config):
    return LEDsStatus(config)
