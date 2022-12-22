class Buzz:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object('pins')

        self.DO = 261.63
        self.RE = 293.66
        self.MI = 329.63
        self.FA = 349.23
        self.SOL = 392
        self.LA = 440
        self.SI = 493.88

        # init PWM. 
        self.sig = ppins.setup_pin('pwm', config.get('pin'))
        self.sig.setup_max_duration(0.)
        self.sig.setup_cycle_time(0.002)

        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('DO', self.cmd_DO)
        gcode.register_command('RE', self.cmd_RE)
        gcode.register_command('MI', self.cmd_MI)
        gcode.register_command('FA', self.cmd_FA)
        gcode.register_command('SOL', self.cmd_SOL)
        gcode.register_command('LA', self.cmd_LA)
        gcode.register_command('SI', self.cmd_SI)
        gcode.register_command('STOP', self.cmd_STOP)

    def cmd_DO(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.DO)
    def cmd_RE(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.RE)
    def cmd_MI(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.MI)
    def cmd_FA(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.FA)
    def cmd_SOL(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.SOL)
    def cmd_LA(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.LA)
    def cmd_SI(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0.5, 1/self.SI)
    def cmd_STOP(self, gcmd):
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.sig.set_pwm(print_time, 0, 0)


def load_config(config):
    return Buzz(config)