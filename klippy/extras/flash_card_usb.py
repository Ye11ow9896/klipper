import os

class FlashCardUSB:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.printer.register_event_handler('klippy:ready', self._handle_ready)

        # variables
        self.mountfolder = config.get('mount_folder_path')
        self.destpath = config.get('gcode_files_path')
        self.usbsection = config.get('usb_section')
        self.flashFolderName = None

        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('USB_FLASH_CHECK', self.cmd_check)
        
    def cmd_check(self, gcmd):
        os.system('rm /home/alex/gcode_files/lol.gcode')

    def _handle_ready(self):
        reactor = self.printer.get_reactor()
        reactor.register_timer(self.load_files, reactor.monotonic()+0.1)

    def load_files(self, eventtime):
        if self._check_usb_flash_card(self.usbsection):
            self.itemlist = os.listdir(self.mountfolder)
            if len(self.itemlist) != 0:
                for item in self.itemlist:
                    if item.endswith('.gcode'):
                        os.system('cp ' + str(self.mountfolder) + '/' + str(item) + ' ' + str(self.destpath) + '/' + str(item))
                    if os.path.isdir(str(self.mountfolder) + '/' + str(item)):
                        self.filecount = 0
                        self.dirItemList = os.listdir(str(self.mountfolder) + '/' + str(item))
                        if len(self.dirItemList) != 0:
                            os.system('cp -r '  + str(self.mountfolder) + '/' + str(item) + ' ' + str(self.destpath) + '/')
                            for file in self.dirItemList:
                                if not file.endswith('.gcode'):
                                    self.filecount += 1
                                    os.system('rm ' + str(self.destpath) + '/' + str(item) + '/' + str(file))
                            if self.filecount == len(self.dirItemList):
                                os.system('rm -r ' + str(self.destpath) + '/' + str(item))
                                self.filecount = 0
                self._unmount_flash_card(self.usbsection)
        return eventtime + 1.

    def _unmount_flash_card(self, section):
        os.system('udisksctl unmount -b /dev/' + str(section))
    
    def _start_automount(self):
        os.system('udiskie &')

    def _check_usb_flash_card(self, section):
        self.filelist = os.listdir('/dev')
        if section in self.filelist:
            return True
        else: 
            return False

def load_config(config):
    return FlashCardUSB(config)
