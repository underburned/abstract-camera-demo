# Прототип демо приложения с абстрактной камерой

Задача: отделить процесс обработки изображений с камеры от процесса захвата изображений с камеры, другими словами, реализовать асинхронный режим работы.

Классы:
- `MainApp` &ndash; основной класс, управляющий всем.
- `CameraGrabber` &ndash; класс, отвечающий только за взаимодействие с камерой посредством SDK камеры. В базовой наивной реализации его основная функциональность &ndash; крутить цикл, на каждой итерации получать буфер из камеры, конвертировать в numpy массив и испускать сигнал со сконвертированным из буфера изображением дальше.
- `FrameProcessor` &ndash; принимает сигнал с изображением, осуществляет обработку независимо от `CameraGrabber`.

<div align="center">
  <img src="images/class_diagram.svg" width="1000" title="Class diagram"/>
  <p style="text-align: center">
    Рисунок 1 &ndash; Диаграмма классов
  </p>
</div>

Объект класса `CameraGrabber` живет в отдельном потоке `QThread`. Объект класса `FrameProcessor` живет в другом отдельном потоке `QThread`.

Взаимодействие между объектами осуществляется с использованием механизма сигнала и слотов PyQt (Qt).

Основное управление осуществляет объект класса `MainApp`. Именно он "решает", когда начинать и останавливать процесс *захвата буфера* с камеры (граббинг, grabbing) и начинать и останавливать процесс *захвата изображения* (capturing). Сам процесс граббинга с точки зрения камеры &ndash; процесс считывания физического сигнала с сенсора камеры и его преобразование в логический сигнал. Как правило, железо и SDK камеры предполагает наличие очереди буферов ограниченного размера, в который камера пишет, а с использованием API SDK мы можем получить указатель/ссылку на буфер через условный метод `grabBuffer()`. Используя объект, возвращаемый данным методом и методом преобразования SDK из буфера в массив байт/numpy массив получить изображение. Далее данное изображение мы передаем через Qt'шный сигнал. На этом итерация цикла в `CameraGrabber` завершается.

## MainApp

В [abs_cam_demo.py](abs_cam_demo.py) ([ссылка на code snippet](abs_cam_demo.py?plain=1#L8)):

```python
class MainApp(QObject):
    start_grabbing = pyqtSignal()
    start_capturing = pyqtSignal()
    stop_capturing = pyqtSignal()
    stop_grabbing = pyqtSignal()
    all_work_is_done = pyqtSignal()
```

- `start_grabbing` &ndash; сигнал "начать процесс граббинга буфера с камеры"
- `start_capturing` &ndash; сигнал "начать процесс захвата изображения с камеры"
- `stop_capturing` &ndash; сигнал "остановить процесс захвата изображения с камеры"
- `stop_grabbing` &ndash; сигнал "остановить процесс граббинга буфера с камеры"
- `all_work_is_done` &ndash; сигнал "завершить работу приложения"

В [abs_cam_demo.py](abs_cam_demo.py) ([ссылка на code snippet](abs_cam_demo.py?plain=1#L18)):

```python
        self.cg = CameraGrabber()
        self.cg_t = QThread(self)
        self.cg_t.start()
        self.cg.moveToThread(self.cg_t)

        self.fp = FrameProcessor()
        self.fp_t = QThread(self)
        self.fp_t.start()
        self.fp.moveToThread(self.fp_t)
```

создаются объекты классов `CameraGrabber` и `FrameProcessor`. Создаются объекты класса `QThread`. Запускаются созданные потоки (`.start()`) Далее созданные объекты классов `CameraGrabber` и `FrameProcessor` помещаются в соответствующие потоки.

> Только после помещения объекта в поток через `.moveToThread()` соединяются сигналы и слоты этого объекта с сигналами и слотами этого же или любых других объектов. В противном случае код внутри слота помещаемого в другой поток объекта будет выполняться в потоке, в котором был создан объект (в нашем случае поток объекта класса `MainApp`).

Перед завершением работы ([ссылка на code snippet](abs_cam_demo.py?plain=1#L43)) необходимо завершить созданные потоки `Qhread`. В `main()` ([ссылка на code snippet](abs_cam_demo.py?plain=1#L63)) сигнал `all_work_is_done` соединяется со слотом `quit()` объекта `app`, в котором (в `app`) и крутится основной цикл событий (event loop) консольного Qt приложения. Слот `quit()` завершает работу приложения.

## CameraGrabber

В [camera_grabber.py](camera_grabber.py) ([ссылка на code snippet](camera_grabber.py?plain=1#L12)):

```python
class CameraGrabber(QObject):
    frame_captured = pyqtSignal(np.ndarray)
    grabbing_started = pyqtSignal()
    grabbing_stopped = pyqtSignal()
    capturing_started = pyqtSignal()
    capturing_stopped = pyqtSignal()
    start_grab_loop = pyqtSignal()
```

- `frame_captured` &ndash; сигнал "изображение захвачено" &ndash; передача сконвертированного из буфера камеры изображения
- `grabbing_started` &ndash; сигнал "процесс граббинга буфера с камеры начат"
- `grabbing_stopped` &ndash; сигнал "процесс граббинга буфера с камеры остановлен"
- `capturing_started` &ndash; сигнал "процесс захвата изображения с камеры начат"
- `capturing_stopped` &ndash; сигнал "процесс захвата изображения с камеры остановлен"
- `start_grab_loop` &ndash; сигнал "начать цикл граббинга буферов с камеры"

Управление процессами начала и остановки граббинга/захвата фреймов помимо сигналов завязана на значениях флагов `grabbing_enabled`, `capturing_enabled` и счетчиков `grabbed_frame_count`, `captured_frame_count`.

## FrameProcessor

В [frame_processor.py](frame_processor.py) ([ссылка на code snippet](frame_processor.py?plain=1#L13)):

```python
class FrameProcessor(QObject):
    process_frame = pyqtSignal(np.ndarray)
```

- `process_frame` &ndash; сигнал "запустить обработку кадра"

В слоте `on_receive_frame` ([ссылка на code snippet](frame_processor.py?plain=1#L23)) пришедший кадр помещается в FIFO очередь и испускается сигнал `process_frame`. В слоте `on_process_frame` ([ссылка на code snippet](frame_processor.py?plain=1#L29)) кадр изымается из очереди, если она не пуста, и обрабатывается.

Код в `FrameProcessor` прототипный: необходимо решить, что делать, если время обработки превышает время получения нового кадра (дропать кадры или помещать в очередь, ограничить размер очереди и т.п.). Реализация зависит от поставленной задачи.

> Необходимо также проработать реализацию остановки процессов захвата и граббинга.