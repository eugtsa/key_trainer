from subprocess import Popen
from subprocess import PIPE
import threading
import queue
import os
import signal


class KeyboardStatus():
    def __init__(self, config):
        self.current_lang = 0
        self._init_queue()
        self.config = config

    def _init_queue(self):
        self.my_queue = queue.Queue()

    def do_reading_lang(self):
        self.lang_proc_started = True
        if not self.config.wm_is_unity:
            self.myLangProcess = Popen(
                'while true; do xset -q' + '|' + 'grep LED' + '|' + ' awk \'{ print $10 }\'' + '|' + 'cut -c5; sleep 0.02; done',
                shell=True, stdout=PIPE)

            while self.lang_proc_started:
                line = self.myLangProcess.stdout.readline()
                if line != '':
                    lang_index = int(line)
                    if lang_index != self.current_lang:
                        self.current_lang = lang_index
                        if self.config.debug:
                            print("Current language is " + line)
                        self.my_queue.put((-1, lang_index))
        else:
            self.myLangProcess = Popen(
                'while true; do setxkbmap -print ' + '|' + ' awk -F"+" \'/xkb_symbols/ {print $2}\'; done', shell=True,
                stdout=PIPE)

            while self.lang_proc_started:
                line = self.myLangProcess.stdout.readline()
                if line != '':
                    if line.find('us') > -1:
                        lang_index = 0
                    else:
                        lang_index = 1
                    if lang_index != self.current_lang:
                        self.current_lang = lang_index
                        if self.config.debug:
                            print
                            "Current language is " + line
                        self.my_queue.put((-1, lang_index))

        self.myLangProcess.terminate()
        if self.config.debug:
            print("Waiting for lang process to stop...")
        self.myLangProcess.wait()
        self.my_queue.queue.clear()

        os.system('killall xinput 2>&1 > /dev/null')
        if self.config.debug:
            print("Stopped language determination process!")

    def doReadingKeys(self):
        self.my_process = Popen(
            'xinput list ' + '|' + '   grep -Po \'id=\K\d+(?=.*slave\s*keyboard)\' ' + '|' + '   xargs -P0 -n1 xinput test',
            shell=True, stdout=PIPE)

        self.proc_started = True

        press_release_dict = {b'key press': 1, b'key relea': 0}

        while self.proc_started:
            xargs_keys = self.my_process.stdout.readline()
            if xargs_keys[:9] in press_release_dict:
                symbol_pressed = press_release_dict[xargs_keys[:9]]
                symbol_index = int(xargs_keys.split(b' ')[-2])

                self.my_queue.put((symbol_index, symbol_pressed))

        self.my_process.terminate()

        if self.config.debug:
            print("Waiting xinput process to stop...")
        self.my_process.wait()

        self.my_queue.queue.clear()
        if self.config.debug:
            print("Stopped xinput process!")

    def begin_scan(self):
        keys_thread = threading.Thread(target=self.doReadingKeys)
        keys_thread.start()
        lang_thread = threading.Thread(target=self.do_reading_lang)
        lang_thread.start()

    def stop_scan(self):
        self.proc_started = False
        self.lang_proc_started = False
        os.kill(self.my_process.pid, signal.SIGQUIT)
