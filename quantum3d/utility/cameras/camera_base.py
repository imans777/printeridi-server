import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except:
        from _thread import get_ident


class CameraEvent(object):
    '''
      An event-like class signaling all actie clients
      when a new frame is available
    '''

    def __init__(self):
        self.events = {}

    def wait(self):
        '''
          invoked from each client's thread
          to wait for the next frame
        '''
        ident = get_ident()
        if ident not in self.events:
            # for a new client -> add entry
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        '''
          invoked by camera thread when
          a new frame is available
        '''
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if the client's evnet is not set, set it
                # and also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if it's already set, it means the client
                # didn't process a previous frame
                # if the event stays set for more than 5 seconds,
                # then assume the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        '''
          invoked from each client's thread
          after a frame was processed        
        '''
        self.events[get_ident()][0].clear()


class CameraBase(object):
    thread = None  # the thread that reads from camera
    frame = None  # current frame of the camera
    last_access_time = 0  # time of last client access
    event = CameraEvent()

    def __init__(self):
        '''
          initialize and start camera thread
        '''
        if CameraBase.thread is None:
            CameraBase.last_access_time = time.time()

            # start camera
            CameraBase.thread = threading.Thread(target=self._thread)
            CameraBase.thread.start()

            # wait till frames become available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        '''
          get new frame
        '''
        CameraBase.last_access_time = time.time()

        CameraBase.event.wait()
        CameraBase.event.clear()

        return CameraBase.frame

    @staticmethod
    def frames():
        '''
          the main generator that produces the camera frames
        '''
        raise RuntimeError('Camera frames is not implemented')
    
    @classmethod
    def _thread(cls):
        '''
            camera background thread
        '''
        print('-> starting camera thread')
        frame_iter = cls.frames()
        for frame in frame_iter:
            CameraBase.frame = frame
            CameraBase.event.set()
            time.sleep(0)

            if time.time() - CameraBase.last_access_time > 10:
                frame_iter.close()
                print('>>> camera goes to sleep due to inactivity')
                break
        CameraBase.thread = None