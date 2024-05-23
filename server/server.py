from flask import Flask, request, jsonify, Blueprint
import ctypes
from ctypes import wintypes

app = Flask(__name__)

status_bp = Blueprint('status', __name__)

# 定义WinAPI函数
user32 = ctypes.WinDLL('user32', use_last_error=True)
GetForegroundWindow = user32.GetForegroundWindow
GetWindowRect = user32.GetWindowRect

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', wintypes.LONG),
        ('top', wintypes.LONG),
        ('right', wintypes.LONG),
        ('bottom', wintypes.LONG),
    ]

def is_fullscreen():
    hwnd = GetForegroundWindow()
    rect = RECT()
    GetWindowRect(hwnd, ctypes.pointer(rect))
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    return rect.left == 0 and rect.top == 0 and rect.right == screen_width and rect.bottom == screen_height

@status_bp.route('/status', methods=['GET'])
def status():
    if is_fullscreen():
        response = "OFFLINE"
    else:
        response = "ONLINE"
    return jsonify({'status': response})

