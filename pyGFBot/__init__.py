# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

import LMGF2
from configs import QuestDB, Pointers

db = QuestDB()
quests = db.quest_db
selected_quests = db.selected
'''tab_names = ['Caixa Misteriosa', 'Monstro', 'Eventos', 'Poder', 'Heróis', 'Coleta', 'Missões', 'Pacotes',
             'Labirinto', 'Ninho', 'Familiar', 'Magnatas', 'Pesquisa', 'Aleatórias', 'Suprimento',
             'Cargueiro', 'Outras']'''
tab_names = set((quest[6] for quest in quests))
tab_names = sorted([tab_name for tab_name in tab_names if tab_name is not None])
pointers = Pointers()


class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('1036x750')
        self.root.configure(bg='#ededed', borderwidth=0, relief='flat',
                            highlightbackground='black', highlightcolor='black')
        self.root.resizable(0, 0)

        self.rootframe = tk.Frame(self.root, bg='#ff0000')
        self.rootframe.place(relx=0, rely=0, relheight=1, relwidth=1)

        self.tab_control = self.create_tabs()

        p_frame = tk.Frame(self.rootframe, bg='#303030')
        p_frame.place(relx=0, rely=.629, relheight=1, relwidth=1)
        self.root.update_idletasks()
        half = self.root.winfo_width() / 2
        p_frame.columnconfigure(0, minsize=half)
        p_frame.columnconfigure(1, minsize=half)

        add_button = tk.Button(p_frame, text='Adicionar às Missões Selecionadas', command=self.add_to_selected,
                               font='-family {Courier} -size 14', bg='#262626', fg='#ffffff',
                               activebackground='#a3e3a3', relief='flat', )
        add_button.grid(row=0, column=0, columnspan=2, sticky='we', padx=5, pady=5)

        selected_frame = tk.Frame(p_frame)
        selected_frame.grid(row=1, column=0, sticky=tk.W + tk.E, rowspan=2, padx=5, pady=5)

        sel_lb_label = tk.Label(selected_frame, text='Missões Selecionadas')
        sel_lb_label.configure(bg='#262626', fg='#ffffff', font='-family {Courier new} -size 12', relief='flat')
        sel_lb_label.pack(fill='both')

        self.selected_lb = tk.Listbox(selected_frame)
        self.selected_lb.pack(fill='both')
        self.selected_lb.configure(activestyle='none', justify='center', relief='flat', selectmode='extended',
                                   font='-family {Courier new} -size 10', bg='#464646', fg='#ffffff',
                                   selectbackground='#a3e3e3', selectforeground='#020202',
                                   highlightcolor='#464646', highlightbackground='#464646')

        remove_button = tk.Button(selected_frame, text='Remover Missões', command=self.remove_item)
        remove_button.configure(bg='#202020', fg='#ffffff', activebackground='#df5454',
                                relief='flat', font='-family {Courier new} -size 10')
        remove_button.pack(fill='both')

        start_button = tk.Button(p_frame, text='Começar', command=self.start)
        start_button.configure(bg='#202020', fg='#ffffff', activebackground='#a3e3e3',
                               relief='flat', font='-family {Arial} -size 30 -weight bold')
        start_button.grid(column=1, row=2, padx=5, pady=5, sticky='nsew')

        pointers_button = tk.Button(p_frame, text='Ponteiros', bg='#202020', fg='#ffffff', relief='flat',
                                    font='-family {Arial} -size 30 -weight bold',
                                    command=ConfigGUI)
        pointers_button.grid(column=1, row=1, pady=5, padx=5, sticky='nswe')

        self.selected_quests_ids = []

        if selected_quests:
            self.insert_selected()

        self.root.mainloop()

    def insert_selected(self):
        for quest in selected_quests:
            text = str(f'{quest[1]}, +{quest[2]} Pontos')
            self.selected_lb.insert('end', text)
            self.selected_quests_ids.append(int(quest[0]))

    def create_tabs(self):
        tab_control = ttk.Notebook(self.rootframe, style='TFrame')
        tabs = []

        for _ in tab_names:
            frame = tk.Frame(tab_control)
            frame.configure(bg='#000000', relief='flat')
            tabs.append(frame)

        for tab, tab_name in zip(tabs, tab_names):
            # print(tab_name)
            tab_control.add(tab, text=tab_name)
            list_box = tk.Listbox(tab)

            with db.connector:
                result = db.cursor.execute('SELECT * from quests where tab_name = ?', [tab_name]).fetchall()
                names = list(set([item[1] for item in result]))
                for name in names:
                    for quest in quests:
                        if quest[6] == tab_name and quest[1] == name:
                            string = f'{quest[0]:<3}| {quest[1]:^57} | +{quest[2]:^3} Pontos | {"0/" + quest[3]:>12}'
                            list_box.insert(tk.END, string)

            list_box.configure(bg='#464646', fg='#ffffff', activestyle='none', justify='left', relief='flat',
                               selectmode='extended', font='-family {Courier New} -size 14', height=17,
                               selectbackground='#a3e3a3', selectforeground='#020202', borderwidth=5,
                               highlightcolor='black', highlightbackground='black',
                               selectborderwidth=2, highlightthickness=0)
            list_box.pack(fill='both')

        tab_control.place(relx=0, rely=0, relwidth=1)
        return tab_control

    def get_selected_items(self):
        result = []
        for k in self.tab_control.children.keys():
            listbox = self.tab_control.children[k].children['!listbox']

            items = [i for i in listbox.curselection()]
            if items:
                for item in items:
                    item_text = listbox.get(item).split('|')
                    text = [str(s).strip() for s in item_text]

                    result.append([f'{text[1]}, {text[2]}', int(text[0])])
        return result

    def add_to_selected(self):
        items = self.get_selected_items()
        for text, q_id in items:
            if q_id in self.selected_quests_ids:
                continue
            else:
                self.selected_quests_ids.append(q_id)
                self.selected_lb.insert('end', text)

    def remove_item(self):
        try:
            index = self.selected_lb.curselection()
            for i in list(index)[::-1]:

                print('Removeu [Id: ' + str(self.selected_quests_ids[i]), self.selected_lb.get(i) + ']')
                self.selected_lb.delete(i)
                self.selected_quests_ids.pop(i)
        except IndexError:
            return

    def start(self):
        print(self.selected_quests_ids)

        db.update_selected(self.selected_quests_ids)
        self.root.destroy()

        LMGF2.GuildFest()


class ConfigGUI:
    def __init__(self):
        from readprocessmemory import Process
        self.lmp = Process('Lords Mobile.exe')
        self.base_address = self.lmp.get_module_address_by_name('GameAssembly.dll')

        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.configure(bg='#303030', borderwidth=0, relief='flat',
                            highlightbackground='black', highlightcolor='black')

        self.time = self.create_inputs('Tempo', 0, 0)
        self.quest_p = self.create_inputs('Pontos da Missão', 0, 1)
        self.quest_r = self.create_inputs('Meta da Missão', 0, 2)
        self.quest_t = self.create_inputs('Tempo da Missão',  1, 0)
        self.name = self.create_inputs('Nome', 1, 1)
        self.populate_inputs(self.time, 'active_time')
        self.populate_inputs(self.quest_p, 'quest_points')
        self.populate_inputs(self.quest_r, 'quest_requirements')
        self.populate_inputs(self.quest_t, 'quest_time')
        self.populate_inputs(self.name, 'player_name')

        save_button = tk.Button(self.root, text='Salvar', width=40, height=1, bg='#202020',
                                font='-family {Segoe UI} -size 10 -weight bold', relief='flat', fg='#fdfdfd',
                                command=self.save_pointers)
        save_button.grid(column=1, ipady=10, pady=10)

        # self.root.mainloop()

    def create_inputs(self, label, row, column):
        label_frame = tk.LabelFrame(self.root, relief='flat', labelanchor="n",
                                    text=label, highlightbackground="#f0f0f0f0f0f0", bg='#404040', fg='#2288fe',
                                    font='-family {Segoe UI} -size 15 -weight bold')

        label_frame.grid_columnconfigure(0, minsize=80)
        label_frame.grid_columnconfigure(1, minsize=80)
        base_input = tk.Entry(label_frame, width=15, relief='solid', justify=tk.CENTER, bg='#505050', fg='#ffffff',
                              font='-family {Segoe UI} -size 12', insertbackground='#ffffff')
        base_input.grid(row=0, column=1, padx=5)

        base_label = tk.Label(label_frame, justify='left', text='Base Pointer: ', bg='#404040', fg='#e1e2e1')
        base_label.grid(row=0, column=0, padx=5, sticky='w', pady=3)

        for i in range(1, 8):
            pointer_label = tk.Label(label_frame, justify='left', text=f'Pointer {i}: ', anchor='w', bg='#404040',
                                     fg='#e1e2e1')
            pointer_label.grid(row=i, column=0, sticky='w', padx=5)

            p_input = tk.Entry(label_frame, width=15, relief='solid', justify=tk.CENTER, bg='#505050', fg='#ffffff',
                               font='-family {Segoe UI} -size 12', insertbackground='#ffffff')
            p_input.grid(row=i, column=1, pady=3, padx=5)

        label_frame.grid(row=row, column=column, padx=10, pady=10, ipadx=10)

        button = tk.Button(label_frame, width=10, font='-family {Segoe UI} -size 10')
        button.configure(text='Testar', bg='#202020', relief='flat', fg='#fdfdfd',
                         command=lambda lf_object=label_frame: self.test_pointers(lf_object))
        button.grid(row=9, pady=3, ipadx=10, padx=5)

        output = tk.Entry(label_frame, width=15, relief='flat', bg='#404040', fg='#ffffff', justify='center',
                          font='-family {Segoe UI} -size 15 -weight bold')
        output.grid(row=9, column=1, pady=3, padx=5)

        return label_frame

    @staticmethod
    def populate_inputs(inputs, populator):
        base_address, pointers_ = pointers.get_pointers(populator)
        values = [base_address] + pointers_
        # print(values)
        index = 0
        for children_name, children in inputs.children.items():
            if type(children) is tk.Entry and children_name != '!entry9':
                children.insert(0, str(hex(values[index]))[2::].upper())
                index += 1

    def test_pointers(self, label_frame):
        output_entry = label_frame.children['!entry9']

        try:
            values = [int(child.get(), 16) for child_name, child in label_frame.children.items()
                      if type(child) is tk.Entry and child_name != '!entry9']
        except ValueError as e:
            print('Value Error', e)
            return

        address = self.lmp.get_pointer(self.base_address + values[0], values[1::])
        result = self.lmp.read_string(address, 40)

        # result = result if result else "???????"

        output_entry.delete(0, tk.END)
        if result:
            output_entry.configure(fg='#22bb55')
            output_entry.insert(0, result)
        else:
            output_entry.configure(fg='#ff5555')
            output_entry.insert(0, '?????????')

    def save_pointers(self):
        names = ['active_time', 'quest_points', 'quest_requirements', 'quest_time', 'player_name']
        label_frames = [lf for _, lf in self.root.children.items() if type(lf) is tk.LabelFrame]

        for item, name in zip(label_frames, names):
            values = [child.get() for child_name, child in item.children.items() if
                      type(child) is tk.Entry and child_name != '!entry9']
            pointers.save_pointers(values, name)
        self.root.destroy()


gui = MainGUI()
