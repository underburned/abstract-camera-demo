from asyncio import Queue
import numpy as np
from PyQt6.QtCore import QMutex, QMutexLocker, QObject, Qt, pyqtSignal, pyqtSlot
from typing import Any, Dict, List, Optional, Tuple, TypeAlias, Union

# Buffer - тип данных буфера из SDK камеры
# Просто заглушка, необходимо заменить Buffer на тип данных буфера из SDK камеры, а эту строчку убрать
Buffer: TypeAlias = bytes
# Просто заглушка, эту строчку убрать
CameraSDK: TypeAlias = None


class FrameProcessor(QObject):
    process_frame = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        self.frame: Optional[np.ndarray] = None
        self.frame_queue: Optional[Queue] = None
        self.processed_frame_count = 0

    @pyqtSlot(np.ndarray)
    def on_receive_frame(self, frame: np.ndarray):
        self.frame_queue.put(frame)
        self.process_frame.emit()

    @pyqtSlot()
    def on_process_frame(self):
        if self.frame_queue.empty():
            pass
        else:
            self.frame = self.frame_queue.get()
            # process frame
            # ...

