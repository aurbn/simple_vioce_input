import sys
import sounddevice as sd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QMessageBox, QPushButton
from PyQt5.QtGui import QIcon
from scipy.io.wavfile import write


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tray Icon App")

        self.recording = False
        self.audio = []

        self.record_button = QPushButton("Start Recording", self)
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.resize(150, 30)
        self.record_button.move(25, 50)

        self.setFixedSize(200, 100)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.setText("Stop Recording")

        self.stream = sd.InputStream(callback=self.audio_callback)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        self.record_button.setText("Start Recording")

        self.stream.stop()
        self.stream.close()

        if self.audio:
            self.save_audio()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio.append(indata.copy())

    def save_audio(self):
        audio_data = np.concatenate(self.audio, axis=0)
        sd.wait()
        write("audio.wav", data=audio_data, rate=44100) #self.stream.samplerate)

        self.audio = []


class TrayIconApp(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_window = MainWindow()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("./icon.png"))  # Replace "icon.png" with the path to your own icon file

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_main_window)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.icon_activated)
        self.tray_icon.show()

    def icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_main_window()

    def show_main_window(self):
        if not self.main_window.isVisible():
            self.main_window.show()

if __name__ == "__main__":
    app = TrayIconApp(sys.argv)
    sys.exit(app.exec_())
