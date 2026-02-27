import numpy as np
from PyQt6.QtCore import QMutex, QMutexLocker, QObject, Qt, pyqtSignal, pyqtSlot
from typing import Any, Dict, List, Optional, Tuple, TypeAlias, Union

# Buffer - тип данных буфера из SDK камеры
# Просто заглушка, необходимо заменить Buffer на тип данных буфера из SDK камеры, а эту строчку убрать
Buffer: TypeAlias = bytes
# Просто заглушка, эту строчку убрать
CameraSDK: TypeAlias = None


class CameraGrabber(QObject):
    frame_captured = pyqtSignal(np.ndarray)
    grabbing_started = pyqtSignal()
    grabbing_stopped = pyqtSignal()
    capturing_started = pyqtSignal()
    capturing_stopped = pyqtSignal()
    start_grab_loop = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.camera = None
        self.buffer: Optional[Buffer] = None
        self.frame: Optional[np.ndarray] = None
        self.grabbing_enabled = False
        self.capturing_enabled = False

        self.grabbed_frame_count = 0
        self.captured_frame_count = 0

    def initialize(self):
        self.camera = CameraSDK()

    @pyqtSlot()
    def on_start_grabbing(self):
        self.grabbing_enabled = True
        self.start_grab_loop.emit()

    @pyqtSlot()
    def on_stop_grabbing(self):
        self.grabbing_enabled = False

    @pyqtSlot()
    def on_start_capturing(self):
        self.start_grab_loop.emit()

    @pyqtSlot()
    def on_stop_capturing(self):
        self.capturing_enabled = False

    @pyqtSlot()
    def grab_loop(self):
        while self.grabbing_enabled:
            buffer = self.camera.get_buffer()
            self.grabbed_frame_count += 1
            if self.grabbed_frame_count == 1:
                print("Grabbing started")
            if self.capturing_enabled:
                frame = CameraSDK.convert_buffer_to_image()
                self.captured_frame_count += 1
                if self.captured_frame_count == 1:
                    print("Capturing started")
                self.frame_captured.emit(frame)
            else:
                if self.captured_frame_count > 0:
                    self.capturing_stopped.emit()
        else:
            print("Grabbing stopped")
            if self.grabbed_frame_count > 0:
                self.grabbing_stopped.emit()

