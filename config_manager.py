__author__ = 'eugtsa'

# -*- coding: utf-8 -*-

import re
from configparser import RawConfigParser
import os


class ConfigManager():
    def __init__(self):
        filename = 'program.conf'
        home = os.path.expanduser("~")
        if os.path.isfile(home + '/.key_trainer/' + filename):
            filename = home + '/.key_trainer/' + filename
        self._read_main_config_from_file(filename)
        self.numOfLangs = int(len(self.index_to_key_name_dict[list(self.index_to_key_name_dict.keys())[0]]) / 2)

    def _read_main_config_from_file(self, path_to_file):
        myParser = RawConfigParser(allow_no_value=True)
        myParser.read(path_to_file)

        keyboard_settings_keys = [x[0] for x in myParser.items("KEYBOARD SETTINGS")]

        self.sections = myParser.sections()

        self.sticky_key_behaviour = False
        self.padx = -1
        self.pady = -1
        self.hide_timeout = 1500

        self.filename = myParser.get("KEYBOARD SETTINGS", 'keyboard_conf_file')
        self.font_name = myParser.get("KEYBOARD SETTINGS", 'font_name')
        self.font_size = myParser.getint("KEYBOARD SETTINGS", 'buttons_font_size')

        self.shift_keys = set()
        for my_str in myParser.get("KEYBOARD SETTINGS", 'keyboard_shift_keys').split(','):
            if my_str != '':
                self.shift_keys.add(int(my_str))

        self.bold_underscored_keys = set()
        for my_str in myParser.get("KEYBOARD SETTINGS", 'keyboard_bold_underscored_keys').split(','):
            if my_str != '':
                self.bold_underscored_keys.add(int(my_str))
        self.create_config_from_file(self.filename)

        sticky_key = myParser.get("KEYBOARD SETTINGS", 'sticky_key_behaviour')
        if sticky_key == '1' or sticky_key == 'True' or sticky_key == 'true':
            self.sticky_key_behaviour = True
        else:
            self.sticky_key_behaviour = False

        if 'button_padx' in keyboard_settings_keys:
            self.padx = myParser.getint("KEYBOARD SETTINGS", 'button_padx')

        if 'button_pady' in keyboard_settings_keys:
            self.pady = myParser.getint("KEYBOARD SETTINGS", 'button_pady')

        if 'hide_timeout' in keyboard_settings_keys:
            self.hide_timeout = myParser.getint("KEYBOARD SETTINGS", 'hide_timeout')

        if "MAIN" in self.sections:
            debug = myParser.get("MAIN", 'debug')
            if debug == '1' or debug == 'True' or debug == 'true':
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False

        self.colored_keys = dict()

        if 'colored_group1' in keyboard_settings_keys:
            self.keys_are_colored = True
            with open(path_to_file) as f:
                lines = f.readlines()
            for line in lines:
                if 'colored_group' in line:
                    splitted_line = line.strip('\n')[line.find('colored_group') + 15:].split(',')
                    group_color = splitted_line[0]
                    group_keys = splitted_line[1:]
                    for key in group_keys:
                        self.colored_keys[int(key)] = group_color

        self.check_for_unity_wm()

    def check_for_unity_wm(self):
        import subprocess

        p = subprocess.Popen('echo $XDG_CURRENT_DESKTOP', shell=True, stdout=subprocess.PIPE)
        output, err = p.communicate()

        if "Unity".encode('utf-8') in output:
            self.wm_is_unity = True
        else:
            self.wm_is_unity = False

    def get_key_name_from_str(self, my_str):
        processed_str = my_str[my_str.find(":") + 2:my_str.rfind(":") - 1]
        result_name = processed_str[0]
        result_list = []
        for index in range(1, len(processed_str)):
            if processed_str[index] == ',':
                if result_name == '':
                    result_name = ","
                else:
                    result_list.append(result_name)
                    result_name = ""
            else:
                result_name += processed_str[index]
        if result_name != '':
            result_list.append(result_name)
        return result_list

    def get_key_name(self, key_index, keyboard_shift, keyboard_lang):
        return self.index_to_key_name_dict[key_index][keyboard_shift * 1 + keyboard_lang * self.numOfLangs]

    def get_key_pos_from_str(self, my_str):
        processed_str = my_str[my_str.rfind(":") + 1:]
        result_list = []
        for pos in processed_str.split(','):
            result_list.append(int(pos))
        return result_list

    def create_config_from_file(self, filename):
        self.index_to_key_name_dict = dict()
        self.index_to_key_pos = dict()
        self.key_pos_to_index = dict()

        self.keys_in_row = dict()
        if '~' in filename:
            from os.path import expanduser
            home = expanduser("~")
            filename = filename.replace("~", home)
        with open(filename) as f:
            lines = f.readlines()
        lines = lines[1:]

        self.numOfRows = 1

        for line in lines:
            line = re.sub('\n\t ', '', line)
            if line != '':
                splitted_line = line.split(':')
                self.index_to_key_name_dict[int(splitted_line[0])] = self.get_key_name_from_str(line)
                position = self.get_key_pos_from_str(line)
                self.index_to_key_pos[int(splitted_line[0])] = position
                self.key_pos_to_index[tuple(position)] = int(splitted_line[0])
                if position[0] not in self.keys_in_row:
                    self.keys_in_row[position[0]] = [position[1]]
                else:
                    self.keys_in_row[position[0]].append(position[1])
                if position[0] > self.numOfRows:
                    self.numOfRows = position[0]

    def get_num_of_rows(self):
        return self.numOfRows

    def get_num_of_keys_in_row(self, row_num):
        if row_num in self.keys_in_row:
            return len(self.keys_in_row[row_num])
        else:
            return 0
