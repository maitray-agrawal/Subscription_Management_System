# -*- coding: utf-8 -*-
import win32file
import win32con

def read_shared_log(filepath, lines_count=80):
    try:
        handle = win32file.CreateFile(
            filepath,
            win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        size = win32file.GetFileSize(handle)
        seek_pos = max(0, size - 40000)
        win32file.SetFilePointer(handle, seek_pos, win32file.FILE_BEGIN)
        _, data = win32file.ReadFile(handle, 40000)
        win32file.CloseHandle(handle)
        text = data.decode('utf-8', errors='ignore')
        lines = text.splitlines()
        for line in lines[-lines_count:]:
            print(line)
    except Exception as e:
        print("Error reading log:", e)

if __name__ == '__main__':
    read_shared_log(r'G:\NixelSoft\Odoo 19.0.20260522\server\odoo.log')
