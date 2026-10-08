import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
from jnius import autoclass
import threading
import time

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.SYSTEM_ALERT_WINDOW,
        Permission.FOREGROUND_SERVICE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ])

CONFIG = {"enabled": False, "fov": 150, "loop_delay": 0.03,
          "color_lower": [0,0,200], "color_upper": [180,80,255]}

state = {"running": True, "overlay": None}


class Main(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(6), **kw)
        with self.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._u, size=self._u)

        self.add_widget(Label(text='AUTO AIMLOCK', font_size='24sp', bold=True,
                              color=(0,1,0.5,1), size_hint_y=None, height=dp(55)))
        self.status = Label(text='OFF', color=(1,0.3,0.3,1),
                            size_hint_y=None, height=dp(35))
        self.add_widget(self.status)

        self.btn = Button(text='START', font_size='20sp', bold=True,
                          background_normal='', background_color=(0.2,0.7,0.2,1),
                          color=(1,1,1,1), size_hint_y=None, height=dp(70))
        self.btn.bind(on_press=self.toggle)
        self.add_widget(self.btn)

        self.add_widget(Label(text='FOV', color=(1,1,1,1), size_hint_y=None, height=dp(30)))
        self.fov = Slider(min=50, max=400, value=150, size_hint_y=None, height=dp(45))
        self.fov.bind(value=self._fov)
        self.add_widget(self.fov)

        self.log = Label(text='Ready...', color=(0.8,0.8,0.8,1),
                         size_hint_y=None, height=dp(45))
        self.add_widget(self.log)

    def _u(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _fov(self, i, v):
        CONFIG["fov"] = int(v)
        if state["overlay"]:
            try:
                state["overlay"].setFov(int(v))
            except Exception:
                pass

    def toggle(self, i):
        if not CONFIG["enabled"]:
            CONFIG["enabled"] = True
            self.btn.text = 'STOP'
            self.btn.background_color = (0.8,0.2,0.2,1)
            self.status.text = 'ON'
            self.status.color = (0.2,1,0.2,1)
            if platform == 'android':
                self.show_overlay()
            threading.Thread(target=self.worker, daemon=True).start()
            Clock.schedule_once(self.go_home, 2.0)
        else:
            CONFIG["enabled"] = False
            self.btn.text = 'START'
            self.btn.background_color = (0.2,0.7,0.2,1)
            self.status.text = 'OFF'
            self.status.color = (1,0.3,0.3,1)
            if platform == 'android':
                self.hide_overlay()

    def show_overlay(self):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            CircleOverlay = autoclass('org.aimlock.CircleOverlay')
            ov = CircleOverlay(PythonActivity.mActivity)
            ov.show()
            ov.setFov(CONFIG["fov"])
            state["overlay"] = ov
        except Exception as e:
            self.log.text = 'Overlay err: ' + str(e)

    def hide_overlay(self):
        try:
            if state["overlay"]:
                state["overlay"].hide()
                state["overlay"] = None
        except Exception:
            pass

    def go_home(self, dt):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            h = Intent(Intent.ACTION_MAIN)
            h.addCategory(Intent.CATEGORY_HOME)
            h.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            PythonActivity.mActivity.startActivity(h)
        except Exception:
            pass

    def worker(self):
        try:
            import cv2
            import numpy as np
        except ImportError:
            self.log.text = 'Missing opencv'
            return
        while CONFIG["enabled"] and state["running"]:
            try:
                os.system('screencap -p /sdcard/s.png')
                f = cv2.imread('/sdcard/s.png')
                if f is None:
                    time.sleep(0.05)
                    continue
                h, w = f.shape[:2]
                cx, cy = w // 2, h // 2
                fov = CONFIG["fov"]
                x1 = max(0, cx - fov); y1 = max(0, cy - fov)
                x2 = min(w, cx + fov); y2 = min(h, cy + fov)
                roi = f[y1:y2, x1:x2]
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                m = cv2.inRange(hsv, np.array(CONFIG["color_lower"]),
                                np.array(CONFIG["color_upper"]))
                k = np.ones((5,5), np.uint8)
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
                m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
                c, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if c:
                    big = max(c, key=cv2.contourArea)
                    if cv2.contourArea(big) > 100:
                        M = cv2.moments(big)
                        if M["m00"]:
                            tx = int(M["m10"]/M["m00"]) + x1
                            ty = int(M["m01"]/M["m00"]) + y1
                            if state["overlay"]:
                                try:
                                    state["overlay"].setTarget(tx, ty)
                                except Exception:
                                    pass
                            os.system('input tap ' + str(tx) + ' ' + str(ty))
                time.sleep(CONFIG["loop_delay"])
            except Exception:
                time.sleep(0.3)


class A(App):
    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.12, 1)
        return Main()
    def on_stop(self):
        state["running"] = False


if __name__ == '__main__':
    A().run()
