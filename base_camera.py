import time
import threading
import socket
from frames import RemoteFrames,SimuFrames
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    #thread = None  # background thread that reads frames from camera
    #frame = None  # current frame is stored here by background thread
    #last_access = 0  # time of last client access to the camera
    #event = CameraEvent()
    dicts = {}
    def __init__(self,addr):
        """Start the background camera thread if it isn't running yet."""
        self.addr = addr
        if addr[0] == '0.0.0.0':
            IsLive = True
            frame_generator = SimuFrames
            if BaseCamera.dicts.has_key(addr) is False:
                thread = threading.Thread(target=self._thread,args=(frame_generator,addr))
                BaseCamera.dicts[addr]=[thread,None,time.time(),CameraEvent(),IsLive]    
                thread.start()
                while self.get_frame() is None:
                    time.sleep(0)
        elif BaseCamera.dicts.has_key(addr) is False:
            IsLive = self.IsRemoteServerLive()
            if IsLive:
                thread = threading.Thread(target=self._thread,args=(RemoteFrames,addr))
                cameraEvent = CameraEvent()
                BaseCamera.dicts[addr]=[thread,None,time.time(),CameraEvent(),IsLive]
                thread.start()
                while self.get_frame() is None:
                    time.sleep(0)
            #else:
                #thread = None; cameraEvent=None
                #BaseCamera.dicts[addr]=[thread,None,time.time(),cameraEvent,IsLive]

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.dicts[self.addr][2] = time.time()

        # wait for a signal from the camera thread
        BaseCamera.dicts[self.addr][3].wait()
        BaseCamera.dicts[self.addr][3].clear()

        return BaseCamera.dicts[self.addr][1]
    def IsRemoteServerLive(self):
        timeout = 5
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setblocking(True)
        s.settimeout(timeout)
        try:
            s.connect(self.addr)
        except socket.timeout:
            return False
        s.send('exit'.encode())
        s.close()
        return True
    def IsServerLive(self):
        """The function can only be called onece """
        return BaseCamera.dicts.has_key(self.addr)
    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls,frames,keys):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = frames(keys)
        print('get frames_iterator.')
        for frame in frames_iterator:
            BaseCamera.dicts[keys][1] = frame
            BaseCamera.dicts[keys][3].set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - BaseCamera.dicts[keys][2] > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        del BaseCamera.dicts[keys]