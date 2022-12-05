ADC_REPORT_TIME = 0.5
ADC_SAMPLE_TIME = 0.001
ADC_SAMPLE_COUNT = 8

class FilamentPresenceSensor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.pin1 = config.get('sens_pin_1')
        self.pin2 = config.get('sens_pin_2')
        self.voltage_empty_sens_1 = config.getfloat('voltage_empty_sens_1') + 0.15
        self.voltage_empty_sens_2 = config.getfloat('voltage_empty_sens_2') + 0.15

        #variables
        self.voltage_value1 = 0 
        self.voltage_value2 = 0
        self.is_printing = False
        self.is_filament_presence_sens_1 = False
        self.is_filament_presence_sens_2 = False
        self.filament_is_over = False

        #printer object
        self.ppins = self.mcu_adc = None
        self.printer.register_event_handler('idle_timeout:printing', self.handle_printing)
        self.printer.register_event_handler('idle_timeout:ready', self.handle_not_printing)
        self.printer.register_event_handler('idle_timeout:idle', self.handle_not_printing)

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

    #Init
    def handle_printing(self, print_time):
        self.is_printing = True

    def handle_not_printing(self, print_time):
        self.is_printing = False

    def adc_callback1(self, read_time, read_value):
        self.voltage_value1 = round(read_value * 3.24, 2)
        #check working on KlipperScreen
        if self.voltage_value1 > self.voltage_empty_sens_1:
            self.is_filament_presence_sens_1 = True
        else:
            self.is_filament_presence_sens_1 = False

        #if self.is_printing and self.voltage_value1 < 2:
        #    self.gcode.run_script('PAUSE')
        #    self.filament_is_over = True
        #    #self.is_filament_presence_sens_1 = False
        #if not self.is_printing and self.voltage_value1 >= 2 and self.filament_is_over == True:
        #    self.gcode.run_script('RESUME')
        #    self.filament_is_over = False
        #    #self.is_filament_presence_sens_1 = True


    def adc_callback2(self,read_time, read_value):
        self.voltage_value2 = round(read_value * 3.24, 2)

        if self.voltage_value2 > self.voltage_empty_sens_2:
            self.is_filament_presence_sens_2 = True
        else:
            self.is_filament_presence_sens_2 = False
        

    def cmd_GetValADC(self, gcmd):
        response = ("Voltage sensor 1: " + str(self.voltage_value1) + "v. Status: " + str(self.is_filament_presence_sens_1) + ' ')
        response += ("Voltage sensor 2: "  + str(self.voltage_value2) + "v. Status: " + str(self.is_filament_presence_sens_2) )
        
        gcmd.respond_info(response)

    def get_status(self, eventtime):
        return {
                "filament_presence_sens_1": bool(self.is_filament_presence_sens_1),
                "filament_presence_sens_2": bool(self.is_filament_presence_sens_2)
        }

def load_config_prefix(config):
    return FilamentPresenceSensor(config)
