import os
import numpy as np
from functools import reduce
from model.taiji.chiper import TaijiChiper
from model.taiji.constant import *

import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MenuPage, EncryptionPage, DecryptionPage, EncryptionResultPage, DecryptionResultPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Stegano LSB", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        encrypt_button = tk.Button(self, text="Encryption",
                            command=lambda: controller.show_frame("EncryptionPage"))
        decrypt_button = tk.Button(self, text="Decryption",
                            command=lambda: controller.show_frame("DecryptionPage"))
        quit_button = tk.Button(self, text='Quit', command= controller.destroy)

        encrypt_button.pack()
        decrypt_button.pack()
        quit_button.pack()

class EncryptionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        title_label = tk.Label(self, text="Encryption...", font=controller.title_font).grid(row=0)

        data_label = tk.Label(self, text='Plain data file').grid(row=1)
        self.data_filename_label = tk.Label(self, text='No file selected..')
        self.data_filename_label.grid(row=1, column=1)
        data_select_button = tk.Button(self, text='Select file', command=self.set_datafile)
        data_select_button.grid(row=2, column=1)

        key_label = tk.Label(self, text='Key (16 char)').grid(row=3)
        self.input_key = tk.StringVar()
        entry_key = tk.Entry(self, textvariable=self.input_key).grid(row=3, column=1)
        
        tk.Label(self, text='Choose mode option:').grid(row=4)
        self.mode_option = tk.IntVar()
        self.mode_option.set(1)
        mode_options = [
            ("EBC", 0),
            ("CBC", 1),
            ("CFB", 2),
            ("OFB", 3)]
        for idx in range(len(mode_options)):
            option_text = mode_options[idx][0]
            val = mode_options[idx][1]
            tk.Radiobutton(self, text=option_text,
                           variable=self.mode_option, value=val).grid(row=4, column=idx+1)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("MenuPage"))
        back_button.grid(row=6)

        encrypt_button = tk.Button(self, text='Process', command=self.do_encryption)
        encrypt_button.grid(row=6, column=1)

    def set_datafile(self):
        self.data_filename = askopenfilename()
        self.data_filename_label.config(text = self.data_filename)

    def do_encryption(self):
        key = self.input_key.get()
        key_bytes = bytearray(key.encode())
        if len(key) <= 0 or len(key) != 16:
            messagebox.showerror("Error", "Key can't be empty and not more than 16 character!")
            return

        with open(self.data_filename, 'rb') as f:
            file_name, file_ext = os.path.splitext(self.data_filename)
            data_bytes = bytearray(f.read())

        modes = ['ecb', 'cbc', 'cfb', 'ofb']
        tj = TaijiChiper(key_bytes, mode=modes[self.mode_option.get()])
        chiper_data = tj.encrypt(data_bytes)
        self.controller.encryption_result = (chiper_data, file_ext)
        self.controller.show_frame('EncryptionResultPage')

class DecryptionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        title_label = tk.Label(self, text="Decryption...", font=controller.title_font).grid(row=0)

        data_label = tk.Label(self, text='Chiper data file').grid(row=1)
        self.data_filename_label = tk.Label(self, text='No file selected..')
        self.data_filename_label.grid(row=1, column=1)
        data_select_button = tk.Button(self, text='Select file', command=self.set_datafile)
        data_select_button.grid(row=2, column=1)

        key_label = tk.Label(self, text='Key (16 char)').grid(row=3)
        self.input_key = tk.StringVar()
        entry_key = tk.Entry(self, textvariable=self.input_key).grid(row=3, column=1)

        tk.Label(self, text='Choose mode option:').grid(row=4)
        self.mode_option = tk.IntVar()
        self.mode_option.set(1)
        mode_options = [
            ("EBC", 0),
            ("CBC", 1),
            ("CFB", 2),
            ("OFB", 3)]
        for idx in range(len(mode_options)):
            option_text = mode_options[idx][0]
            val = mode_options[idx][1]
            tk.Radiobutton(self, text=option_text,
                           variable=self.mode_option, value=val).grid(row=4, column=idx+1)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("MenuPage"))
        back_button.grid(row=6)

        decrypt_button = tk.Button(self, text='Process', command=self.do_decryption)
        decrypt_button.grid(row=6, column=1)

    def set_datafile(self):
        self.data_filename = askopenfilename()
        self.data_filename_label.config(text = self.data_filename)

    def do_decryption(self):
        key = self.input_key.get()
        key_bytes = bytearray(key.encode())
        if len(key) <= 0 or len(key) != 16:
            messagebox.showerror("Error", "Key can't be empty and not more than 16 character!")
            return

        with open(self.data_filename, 'rb') as f:
            file_name, file_ext = os.path.splitext(self.data_filename)
            data_bytes = bytearray(f.read())
        modes = ['ecb', 'cbc', 'cfb', 'ofb']
        tj = TaijiChiper(key_bytes, mode=modes[self.mode_option.get()])
        plain_data = tj.decrypt(data_bytes)
        self.controller.decryption_result = (plain_data, file_ext)
        self.controller.show_frame('DecryptionResultPage')

class EncryptionResultPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        title_label = tk.Label(self, text="Encryption Result", font=controller.title_font).grid(row=0)
        
        result_label = tk.Label(self, text="Result cant be displayed because of character encoding \n Save it to view the result!!")
        result_label.grid(row=1)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ExtractPage"))
        back_button.grid(row=6)

        save_button = tk.Button(self, text="Save Result", command=self.save_result)
        save_button.grid(row=6, column=1)

    def save_result(self):
        data_bytes, file_ext = self.controller.encryption_result
        filename = asksaveasfilename(defaultextension=file_ext, filetypes=(("txt", "*.txt"), ("java", ".java"), ("All Files", "*.*")))
        with open(filename, "wb") as f:
            f.write(data_bytes)
        messagebox.showinfo("Sucess", "The result succesfully saved!")
        self.controller.show_frame("MenuPage")

class DecryptionResultPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        title_label = tk.Label(self, text="Decryption Result", font=controller.title_font).grid(row=0)
        
        result_label = tk.Label(self, text="Result cant be displayed because of character encoding \n Save it to view the result!!")
        result_label.grid(row=1)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ExtractPage"))
        back_button.grid(row=6)

        save_button = tk.Button(self, text="Save Result", command=self.save_result)
        save_button.grid(row=6, column=1)

    def save_result(self):
        data_bytes, file_ext = self.controller.decryption_result
        filename = asksaveasfilename(defaultextension=file_ext, filetypes=(("txt", "*.txt"), ("java", ".java"), ("All Files", "*.*")))
        with open(filename, "wb") as f:
            f.write(data_bytes)
        messagebox.showinfo("Sucess", "The result succesfully saved!")
        self.controller.show_frame("MenuPage")

def main():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()