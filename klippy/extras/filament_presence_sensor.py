ADC_REPORT_TIME = 0.5
ADC_SAMPLE_TIME = 0.001
ADC_SAMPLE_COUNT = 8

class FilamentPresenceSensor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.pin1 = config.get('sens_pin_1')
        self.pin2 = config.get('sens_pin_2')
        self.error = config.getfloat('error')
        self.voltage_empty_sens_1 = config.getfloat('voltage_empty_sens_1', 2.05, minval=0., maxval=6.) + self.error
        self.voltage_empty_sens_2 = config.getfloat('voltage_empty_sens_2', 1.69, minval=0., maxval=6.) + self.error

        #variables
        self.voltage_value1 = 0 
        self.voltage_value2 = 0
        self.is_filament_presence_sens_1 = False
        self.is_filament_presence_sens_2 = False
        self.filament_is_over = False

        #printer object
        self.ppins = self.mcu_adc = None
        self.printer.register_event_handler('idle_timeout:ready', self._handle_ready)

        #Start ADC
        self.ppins = self.printer.lookup_object('pins')
        self.mcu_adc = self.ppins.setup_pin('adc', self.pin1)
        self.mcu_adc.setup_minmax(ADC_SAMPLE_TIME, ADC_SAMPLE_COUNT)
        self.mcu_adc.setup_adc_callback(ADC_REPORT_TIME, self.adc_callback1)
        self.mcu_adc2 = self.ppins.setup_pin('adc', self.pin2)
        self.mcu_adc2.setup_minmax(ADC_SAMPLE_TIME, ADC_SAMPLE_COUNT)
        self.mcu_adc2.setup_adc_callback(ADC_REPORT_TIME, self.adc_callback2)

        #register commands
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_mux_command("VOLTAGE_VALUE_SENSOR", "SENSOR", 
                                            self.name, self.cmd_GetValADC)

        self.gcode.register_mux_command("CALIBRATE", "SENSOR", 
                                            self.name, self.cmd_CalibrateSensors)

    def _handle_ready(self, print_time):
        if self.voltage_value1 <= self.voltage_empty_sens_1:
            self.voltage_empty_sens_1 = self.voltage_value1 + self.error
        if self.voltage_value2 <= self.voltage_empty_sens_2:
            self.voltage_empty_sens_2 = self.voltage_value2 + self.error

    def adc_callback1(self, read_time, read_value):
        self.voltage_value1 = round(read_value * 3.24, 2)
        #check working on KlipperScreen
        if self.voltage_value1 > self.voltage_empty_sens_1:
            self.is_filament_presence_sens_1 = True
        else:
            self.is_filament_presence_sens_1 = False

    def adc_callback2(self,read_time, read_value):
        self.voltage_value2 = round(read_value * 3.24, 2)

        if self.voltage_value2 > self.voltage_empty_sens_2:
            self.is_filament_presence_sens_2 = True
        else:
            self.is_filament_presence_sens_2 = False
        
    def cmd_GetValADC(self, gcmd):
        response = ("Voltage sensor 1: " + str(self.voltage_value1) + "v. Status: " + str(self.is_filament_presence_sens_1) + ' \n')
        response += ("Voltage empty sensor 1: " + str(self.voltage_empty_sens_1) + '\n')
        response += ("Voltage sensor 2: "  + str(self.voltage_value2) + "v. Status: " + str(self.is_filament_presence_sens_2) + '\n')
        response += ("Voltage empty sensor 2: " + str(self.voltage_empty_sens_2) + '\n')
        
        gcmd.respond_info(response)

    def cmd_CalibrateSensors(self, gcmd):
        fullname = ("filament_presence_sensor " + str(self.name))

        configfile = self.printer.lookup_object('configfile')
        configfile.set(fullname, 'voltage_empty_sens_1', "%.2f" % (self.voltage_value1,))
        configfile.set(fullname, 'voltage_empty_sens_2', "%.2f" % (self.voltage_value2,))

        gcmd.respond_info(
            "New voltage value on empty sensors: \n" 
            "sensor 1: %.2f V; sensor 2: %.2f V \n"  
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer." % (self.voltage_value1, self.voltage_value2))

    def get_status(self, eventtime):
        return {
                "filament_presence_sens_1": bool(self.is_filament_presence_sens_1),
                "filament_presence_sens_2": bool(self.is_filament_presence_sens_2)
        }

def load_config_prefix(config):
    return FilamentPresenceSensor(config)


