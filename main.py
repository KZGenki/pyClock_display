# PyClock Version 3.0
import tkinter.font
from tkinter import *
from datetime import datetime
import threading
import time
import socket


received_value = -1
timeout_max = 5
slow_update = 0.5
fast_update = 0.1

def info_tick():
    global info, timeout_max, slow_update, fast_update
    old_volume = received_value

    timeout = 0
    current_update = slow_update
    while True:
        current_volume = received_value
        try:
            if current_volume is not old_volume:
                old_volume = current_volume
                timeout = 0
                current_update = fast_update
                try:
                    int(current_volume)
                    info.set("Vol:" + str(current_volume))
                except ValueError:
                    # old_volume = -1
                    info.set(current_volume)
            elif current_volume == old_volume and timeout < timeout_max:
                timeout = timeout + current_update
                current_update = fast_update
            elif current_volume == old_volume and timeout >= timeout_max:
                current_update = slow_update
                info.set('')
            # print("info_tick: " + str(current_volume))
        except RuntimeError:
            break
        time.sleep(current_update)


def receiver():
    global info, received_value, timeout_max, slow_update, fast_update
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5015
    #UDP_IP = "127.0.0.1"
    #UDP_PORT = 5020
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    old_volume = -1

    timeout = 0
    current_update = slow_update
    while True:
        data, addr = sock.recvfrom(1024)
        # print(data)
        current_volume = data.decode('ASCII')
        try:
            if current_volume is not old_volume:
                old_volume = current_volume
                timeout = 0
                current_update = fast_update
                received_value = current_volume
            if current_volume == old_volume and timeout < timeout_max:
                timeout = timeout + current_update
                current_update = fast_update
            elif current_volume == old_volume and timeout >= timeout_max:
                current_update = slow_update
                received_value = -1
                data = None
                #info.set('')
            # print("receiver: " + str(current_volume))
        except RuntimeError:
            break
        time.sleep(current_update)


evening_winter = ['21', '22', '23', '05','06','07']
evening_summer = ['21', '22', '23', '05']
evening = evening_summer
night = ['00', '01', '02', '03', '04']


def apply_theme(hour):
    if hour in evening:
        evening_theme()
    elif hour in night:
        night_theme()
    else:
        day_theme()


def day_theme():
    set_theme()


def evening_theme():
    set_theme('black', 'DarkOrange3')


def night_theme():
    set_theme('black', 'maroon')


def set_theme(background='white', foreground='black'):
    main_window.configure(bg=background)
    clock.configure(fg=foreground, bg=background)
    display_info.configure(fg=foreground, bg=background)
    pass


def clock_tick():
    global clock_string
    old_hour = 'NN'
    while True:
        now = datetime.now()
        new_hour = now.strftime("%H")
        try:
            if new_hour is not old_hour:
                old_hour = new_hour
                apply_theme(new_hour)
            clock_string.set(now.strftime("%H:%M"))
        except RuntimeError:
            break
        # print(clock_string.get())
        time.sleep(1)

try:
	main_window = Tk()
	clock_string = StringVar()
	clock_string.set("init")
	info = StringVar()
	info.set("info")
	main_window.geometry('800x480')
	main_window.attributes("-fullscreen", True) # pi thing to make window fullscreen instead of windowed
	clock_font = tkinter.font.Font(family="Arial", size=190, weight='bold')
	info_font = tkinter.font.Font(size=72, weight='bold')
	clock = Label(main_window, textvariable=clock_string, font=clock_font)
	clock.pack()
	display_info = Label(main_window, textvariable=info, font=info_font)
	display_info.pack()

	set_theme('red', 'blue')
	t_clock = threading.Thread(target=clock_tick)
	t_clock.start()
	t_info = threading.Thread(target=info_tick)
	t_info.start()
	t_receiver = threading.Thread(target=receiver)
	t_receiver.start()
	main_window.mainloop()
	t_clock.join()
	t_info.join()
	t_receiver.join()
except:
	print("")
