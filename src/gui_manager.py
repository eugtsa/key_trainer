__author__ = 'eugtsa'

from tkinter import Frame, Button, FALSE, LEFT, SUNKEN, RAISED
from tkinter import font

class GuiManager():
    def __init__(self, master, config, queue, key_trainer):
        self.master = master

        master.title("Keyboard")
        master.attributes('-topmost', 1)
        master.resizable(width=FALSE, height=FALSE)

        self.shift_key_codes = config.shift_keys
        self.config = config
        self.queue = queue
        self.currentLang = 0
        self.key_trainer = key_trainer
        self.block_resizing = False

        self.gui_all_buttons = dict()
        self.gui_rows = dict()
        self.gui_row_buttons = dict()
        self.sticky_key_behaviour = self.config.sticky_key_behaviour
        self.last_sticky_button = list(self.config.index_to_key_name_dict.keys())[0]

        self.button_font = font.Font(family=config.font_name, size=config.font_size)
        self.bold_underscored_button_font = font.Font(family=config.font_name, size=config.font_size, weight='bold',
                                                      underline=1)

        for row_index in range(1, config.get_num_of_rows() + 1):
            self.gui_rows[int(row_index)] = Frame(master)
            self.gui_row_buttons[int(row_index)] = []
            for button_num in range(1, config.get_num_of_keys_in_row(row_index) + 1):
                new_button = Button(self.gui_rows[int(row_index)])
                if self.config.padx != -1:
                    new_button.config(padx=self.config.padx)
                if self.config.pady != -1:
                    new_button.config(pady=self.config.pady)
                if (row_index, int(button_num)) in config.key_pos_to_index:
                    self.gui_all_buttons[config.key_pos_to_index[(row_index, int(button_num))]] = new_button
                self.gui_row_buttons[int(row_index)].append(new_button)
                new_button.pack(side=LEFT)

            self.gui_rows[int(row_index)].pack()
        self.reconfigure_text_on_buttons(config, shift_pressed=0, lang=0)

        if len(self.config.colored_keys) != 0:
            for button_index in self.config.colored_keys:
                if button_index in self.gui_all_buttons:
                    self.gui_all_buttons[button_index].configure(bg=self.config.colored_keys[button_index])

        master.update_idletasks()

        self.default_geometry = self.parse_geometry(master.geometry())
        master.bind('<Enter>', self.mouse_entered)
        master.bind('<Motion>', self.mouse_entered)

    def resize_window_back(self):
        self.block_resizing = False
        self.resize_y_of_window(self.default_geometry[1])

    def parse_geometry(self, in_geometry):
        geometry_x_y = in_geometry[:in_geometry.find('+')]
        geometry_x_y = geometry_x_y.split('x')
        window_size = (int(geometry_x_y[0]), int(geometry_x_y[1]))
        return window_size

    def resize_y_of_window(self, y):
        if y < 0:
            y = 0
        self.master.geometry(str(self.default_geometry[0]) + 'x' + str(y))
        self.master.update_idletasks()

    def mouse_entered(self, event):
        self.resize_y_of_window(event.y - 15)
        if not self.block_resizing:
            self.block_resizing = True
            self.master.after(self.config.hide_timeout, self.resize_window_back)

    def reconfigure_text_on_buttons(self, config, shift_pressed, lang):
        for row_index in range(1, config.get_num_of_rows() + 1):
            configured_buttons = dict((k, v) for k, v in config.key_pos_to_index.items() if k[0] == row_index)
            for configured_button_pos in configured_buttons:
                key_index = configured_buttons[configured_button_pos]
                self.gui_all_buttons[key_index]['font'] = self.button_font
                self.gui_all_buttons[key_index].configure(text=config.get_key_name(key_index, shift_pressed, lang))
        for key_index in config.bold_underscored_keys:
            if key_index in self.gui_all_buttons:
                self.gui_all_buttons[key_index]['font'] = self.bold_underscored_button_font

    def process_queue(self):
        while not self.queue.empty():
            msg = self.queue.get(0)
            if msg[0] == -1:  # -1 message is for changing language
                self.currentLang = int(msg[1])
                if self.config.debug:
                    print("Changed lang!")
                self.reconfigure_text_on_buttons(self.config, 0, msg[1])

            if msg[0] in self.gui_all_buttons:
                if msg[0] in self.shift_key_codes:
                    self.reconfigure_text_on_buttons(self.config, msg[1], self.currentLang)
                if msg[1] == 1:
                    self.gui_all_buttons[msg[0]].config(relief=SUNKEN)
                    if self.sticky_key_behaviour:
                        if self.last_sticky_button != msg[0]:
                            self.gui_all_buttons[self.last_sticky_button].config(relief=RAISED)
                        self.last_sticky_button = msg[0]
                else:
                    if not self.sticky_key_behaviour:
                        self.gui_all_buttons[msg[0]].config(relief=RAISED)
            if self.config.debug:
                print(msg)

    def start(self):
        self.mainloop()
