[app]
title = AutoAimlock
package.name = autoaimlock
package.domain = org.aimlock
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,java
version = 1.0
requirements = python3,kivy==2.2.1,opencv,numpy,pyjnius,android,plyer
orientation = portrait
fullscreen = 0
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.archs = arm64-v8a
android.allow_backup = True
p4a.branch = develop
p4a.bootstrap = sdl2
android.add_src = src
