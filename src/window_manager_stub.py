"""Stub module for win32 dependencies for non-Windows platforms."""

# Stub constants
SW_RESTORE = 9

def IsWindowVisible(hwnd):
    return True

def GetWindowRect(hwnd):
    return (0, 0, 800, 600)

def MoveWindow(hwnd, x, y, width, height, repaint):
    pass

def GetWindowText(hwnd):
    return "Test Window"

def ShowWindow(hwnd, cmd):
    pass

def SetForegroundWindow(hwnd):
    pass

def IsIconic(hwnd):
    return False

def EnumWindows(callback, data):
    pass

def GetWindowThreadProcessId(hwnd):
    return (0, 1234)
