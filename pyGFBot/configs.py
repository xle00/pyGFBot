# -*- coding: utf-8 -*-
import sqlite3


class SqlConnector:
    def __init__(self):
        self.connector = sqlite3.connect('quests.db')
        self.cursor = self.connector.cursor()


class QuestDB(SqlConnector):
    def __init__(self):
        super(QuestDB, self).__init__()

    @property
    def quest_db(self):
        quests = self.cursor.execute('select * from quests').fetchall()
        return quests

    @property
    def selected(self):
        quests = self.cursor.execute('select * from quests where is_selected = 1').fetchall()
        return quests

    def update_selected(self, quest_id_list):
        with self.connector:
            self.cursor.execute('UPDATE quests SET is_selected = Null')
            for quest in quest_id_list:
                self.cursor.execute('update quests SET is_selected = 1 where quest_id = ?', [quest])


class Pointers(SqlConnector):
    def __init__(self):
        super(Pointers, self).__init__()

    def get_pointers(self, pointer_name):
        pointers = self.cursor.execute('SELECT * from pointers where pointer_name = ?', [pointer_name]).fetchone()
        base_pointer = int(pointers[1], 16)
        _pointers = [int(i, 16) for i in pointers[2::]]
        return base_pointer, _pointers

    def save_pointers(self, pointer_list, pointer_name):
        with self.connector:
            query = '''
                UPDATE pointers
                SET base_pointer = ?, pointer1 = ?, pointer2 = ?, pointer3 = ?, pointer4 = ?, pointer5 = ?,
                pointer6 = ?, pointer7 = ? WHERE pointer_name = ?
            '''
            self.cursor.execute(query, pointer_list + [pointer_name])
