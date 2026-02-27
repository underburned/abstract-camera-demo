from PyQt6.QtCore import QCoreApplication, QMutex, QMutexLocker, QObject, Qt, QThread, pyqtSignal, pyqtSlot
import sys
from typing import Any, Dict, List, Optional, Tuple, Union
from camera_grabber import CameraGrabber
from frame_processor import FrameProcessor


class MainApp(QObject):
    start_grabbing = pyqtSignal()
    start_capturing = pyqtSignal()
    stop_capturing = pyqtSignal()
    stop_grabbing = pyqtSignal()
    all_work_is_done = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.cg = CameraGrabber()
        self.cg_t = QThread(self)
        self.cg_t.start()
        self.cg.moveToThread(self.cg_t)

        self.fp = FrameProcessor()
        self.fp_t = QThread(self)
        self.fp_t.start()
        self.fp.moveToThread(self.fp_t)

    def initialize(self):

        # Connect signals and slots
        self.start_grabbing.connect(self.cg.on_start_grabbing, Qt.ConnectionType.QueuedConnection)
        self.start_capturing.connect(self.cg.on_start_capturing, Qt.ConnectionType.QueuedConnection)
        self.stop_capturing.connect(self.cg.on_stop_capturing, Qt.ConnectionType.QueuedConnection)
        self.stop_grabbing.connect(self.cg.on_stop_grabbing, Qt.ConnectionType.QueuedConnection)
        self.cg.start_grab_loop.connect(self.cg.grab_loop, Qt.ConnectionType.QueuedConnection)
        self.cg.grabbing_started.connect(self.on_grabbing_started, Qt.ConnectionType.QueuedConnection)
        self.cg.grabbing_stopped.connect(self.on_grabbing_stopped, Qt.ConnectionType.QueuedConnection)
        self.cg.frame_captured.connect(self.fp.on_receive_frame, Qt.ConnectionType.QueuedConnection)

        self.cg.initialize()
        self.start_grabbing.emit()

    def free_resources(self):
        self.fp_t.quit()
        self.fp_t.wait()

        self.cg_t.quit()
        self.cg_t.wait()
        self.all_work_is_done.emit()

    @pyqtSlot()
    def on_grabbing_started(self):
        self.start_capturing.emit()

    @pyqtSlot()
    def on_grabbing_stopped(self):
        self.free_resources()


def main():
    app = QCoreApplication(sys.argv)
    ma = MainApp()
    ma.all_work_is_done.connect(app.quit)


if __name__ == '__main__':
    main()
