#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'eugtsa'

from src.config_manager import ConfigManager
from src.gui_manager import GuiManager
from src.keybard_status import KeyboardStatus


class ThreadedClient:
    def __init__(self, master):
        self.master = master

        self.config = ConfigManager()
        self.key_trainer = KeyboardStatus(self.config)

        self.master.protocol('WM_DELETE_WINDOW', self.kill_and_destroy)

        self.gui_manager = GuiManager(master, self.config, self.key_trainer.my_queue, self.key_trainer)

        self.key_trainer.begin_scan()

        self.running = 1
        self.periodic_call()

    def kill_and_destroy(self):
        self.running = 0
        self.key_trainer.stop_scan()
        if self.config.debug:
            print("Stopping scan...")
        self.master.destroy()

    def periodic_call(self):
        self.gui_manager.process_queue()
        if not self.running:
            self.kill_and_destroy()
        self.master.after(20, self.periodic_call)


if __name__ == '__main__':
    try:
        import tkinter

        root = tkinter.Tk()

        root.attributes("-alpha", 0.5)
        client = ThreadedClient(root)
        root.mainloop()
    except ImportError:
        print("Please install tkinter for python, on Ubuntu, Mint do following:\n"
              "sudo apt-get install python-tk")
