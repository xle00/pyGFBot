# -*- coding: utf-8 -*-
import os
from time import strptime, sleep

import win32api
import win32con
import win32gui
from PIL import ImageGrab
from configs import QuestDB, Pointers
from pushbullet import PushBullet
from readprocessmemory import Process

db = QuestDB()
pointers = Pointers()


class LMReadMemory:
    def __init__(self):
        self.lm = Process('Lords Mobile.exe')
        self.dll_base_address = self.lm.get_module_address_by_name('GameAssembly.dll')
        self.get_pointer = self.lm.get_pointer
        self.read_str = self.lm.read_string
        self.name = self.get_username

    def get_active_time(self):
        base_pointer, pointers_ = pointers.get_pointers('active_time')

        address = self.get_pointer(self.dll_base_address + base_pointer, pointers_)
        value = self.read_str(address, 5)
        time = strptime(value, '%M:%S').tm_sec + strptime(value, '%M:%S').tm_min * 60
        return time

    def get_mission_details(self):
        base_pointer, pointers_ = pointers.get_pointers('quest_points')
        quest_points_address = self.get_pointer(self.dll_base_address + base_pointer, pointers_)

        base_pointer, pointers_ = pointers.get_pointers('quest_requirements')
        quest_reqs_address = self.get_pointer(self.dll_base_address + base_pointer, pointers_)

        base_pointer, pointers_ = pointers.get_pointers('quest_time')
        quest_time_address = self.get_pointer(self.dll_base_address + base_pointer, pointers_)

        points = self.read_str(quest_points_address, 4)
        requirements = self.get_pointer(quest_reqs_address, 20)
        quest_time = self.get_pointer(quest_time_address, 11)

        result = {'Points': points, 'Requirements': requirements, 'Time': quest_time}

        return result

    @property
    def get_username(self):
        base_pointer, pointers_ = pointers.get_pointers('player_name')

        address = self.get_pointer(self.dll_base_address + base_pointer, pointers_)
        value = self.read_str(address, 12)
        username = ''
        for char in value:
            if ord(char) == 0:
                break
            username += char
        return username


class Mouse:
    @staticmethod
    def set_pos(x, y):
        win32api.SetCursorPos((x, y))

    @staticmethod
    def get_pos():
        return win32api.GetCursorPos()

    @staticmethod
    def wheel(clicks, x=None, y=None, interval=0.001):
        wheelturns = abs(clicks)
        if x and y:
            Mouse.set_pos(x, y)

        for _ in range(wheelturns):
            if clicks > 0:
                win32api.mouse_event(0x0800, 0, 0, -1, 0)
            elif clicks < 0:
                win32api.mouse_event(0x0800, 0, 0, 1, 0)
            sleep(interval)

    @staticmethod
    def left_click(x=None, y=None, lenght=0.000):
        if not x and not y:
            x, y = Mouse.get_pos()
        Mouse.set_pos(x, y)
        win32api.mouse_event(0x02, 0, 0, 0, 0)
        sleep(lenght)
        win32api.mouse_event(0x04, 0, 0, 0, 0)


class GuildFest(LMReadMemory):
    def __init__(self):
        super(GuildFest, self).__init__()
        self.x_coords = [294, 491, 661]
        self.y_coords = [456, 695, 676, 701, 694, 712, 710]
        self.selected = db.selected
        self.hwnd = win32gui.FindWindow('UnityWndClass', 'Lords Mobile')
        self.activate_window()
        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        print(self.get_username)
        # self.start()

    def activate_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def get_the_mission(self, slot=None, text=''):
        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        if slot is not None:
            self.go_to_slot(slot)
        print(f'Pegando a Missão: {text}')
        Mouse.left_click(self.lm_pos[0] + 867, self.lm_pos[1] + 679)

        pb.push_note(f'Missão Pronta [{self.get_username}]', text)
        pb.push_note(f'Missão Pronta [{self.get_username}]', text, email='thallesrafael1402@gmail.com')

        sleep(4)

        bbox = (self.lm_pos[0] + 764, self.lm_pos[1] + 329, self.lm_pos[0] + 1114, self.lm_pos[1] + 713)
        img = ImageGrab.grab(bbox=bbox)
        img.save('tempimage.jpeg')

        pb.push_img('tempimage.jpeg')
        pb.push_img('tempimage.jpeg', email='thallesrafael1402@gmail.com')
        os.remove('tempimage.jpeg')

        exit()

    def get_quest_name(self):
        quest = self.get_mission_details()

        query_result = db.cursor.execute(
            'SELECT * from quests where quest_points = ? and quest_requirements = ? and quest_time = ?',
            (int(quest['Points']), quest['Requirements'], quest['Time'])).fetchone()

        quest_id, quest_name, quest_points, _, _, is_selected, _ = query_result

        text = f'{quest_name}, +{quest_points}'
        if is_selected:
            self.get_the_mission(text=text)
        return text

    def go_to_slot(self, slot):
        wheel_turns = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 7, 7: 7, 8: 7, 9: 14, 10: 14, 11: 14, 12: 21, 13: 21,
                       14: 21, 15: 28, 16: 28, 17: 28, 18: 35, 19: 35, 20: 35}
        self.activate_window()

        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        sleep(.01)
        x, y = self.x_coords[slot % 3], self.y_coords[slot // 3]

        if slot <= 5:
            Mouse.left_click(self.lm_pos[0] + x, self.lm_pos[1] + y)
            return
        else:
            Mouse.wheel(wheel_turns[slot])
            Mouse.left_click(self.lm_pos[0] + x, self.lm_pos[1] + y)
            Mouse.wheel(-wheel_turns[slot])
        sleep(.1)

    def get_sorted_time_list(self, board_times=None):
        if not board_times:
            board_times = self.get_board()

        desc_times = sorted([i for i in board_times.values()], reverse=True)
        print(desc_times)
        sorted_board_times = [0 for _ in desc_times]
        print(sorted_board_times)

        for slot, time in board_times.items():
            print(slot, time)
            time_index = desc_times.index(time)
            sorted_board_times[time_index] = slot

        print(sorted_board_times)
        return sorted_board_times

    def start(self):
        if not self.selected:
            print('Nenhuma Missão Selecionada\n')
        else:
            print('Missões Selecionadas:')
            for sq in self.selected:
                print(f'{sq[1]}: {"+" + str(sq[2]):<4} {"0/" + sq[3]:<12} {sq[4]}')
            print('')

        self.lm_pos = win32gui.GetWindowRect(self.hwnd)
        sorted_slots = self.get_sorted_time_list()
        bbox = (self.lm_pos[0] + 885, self.lm_pos[1] + 354, self.lm_pos[0] + 886, self.lm_pos[1] + 355)

        while sorted_slots:
            closest_slot = sorted_slots.pop()
            self.go_to_slot(closest_slot)

            brightness = self.check_pixel_area_brightness(bbox)
            if brightness < 127:
                active_time = self.get_active_time()
                print('Próxima missão em {}s ({:02d}:{:02d})'.format(active_time, active_time // 60, active_time % 60))
                if active_time > 10:
                    sleep(active_time - 10)
                    self.activate_window()
                    # pyautogui.moveTo(519, 521, 0, _pause=False)
                    Mouse.set_pos(519, 521)

                while brightness < 127:
                    brightness = self.check_pixel_area_brightness(bbox)
                details = self.get_quest_name()
                print(details + '\n')
            else:
                details = self.get_quest_name()
                print(details + '\n')

        self.start()

    @staticmethod
    def check_pixel_area_brightness(area):
        img = ImageGrab.grab(bbox=area, all_screens=True)
        pixelsavg = 0
        for pixel in img.getdata():
            pixelavg = (pixel[0] + pixel[1] + pixel[2]) / 3
            pixelsavg += pixelavg
        pixelsavg /= len(img.getdata())
        return pixelsavg

    def get_board(self):
        self.activate_window()
        lmpos = win32gui.GetWindowRect(self.hwnd)
        bbox = (lmpos[0] + 885, lmpos[1] + 354, lmpos[0] + 886, lmpos[1] + 355)
        mousewheelcounter = 0
        quests_timers = {}

        for i in range(1, 21):
            x_index = i % 3
            y_index = i // 3

            Mouse.left_click(self.lm_pos[0] + self.x_coords[x_index], self.lm_pos[1] + self.y_coords[y_index])

            brightness = self.check_pixel_area_brightness(bbox)

            if brightness > 127:
                quest_name = self.get_quest_name()
                print(quest_name, '\n')
            else:
                result = self.get_active_time()
                quests_timers.update({i: result})

            if 5 <= i < 20 and i % 3 == 2:
                Mouse.wheel(7)
                mousewheelcounter += 7
        Mouse.wheel(-35)
        return quests_timers


pb = PushBullet()


def main():
    GuildFest()


if __name__ == '__main__':
    main()
    # lm = LMReadMemory()
    # while True:
    #    print(lm.get_active_time())
    #    sleep(1)
