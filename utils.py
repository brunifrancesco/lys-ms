



import redis
import functools
import os
import subprocess
import signal
from bottle import abort


def start_stream_and_store(*args, **kwargs):
    """
    Start stream running the yes command in background;
    store the PID in Redis along with the related port
    """
    try:
        if os.path.isfile("sdps/%s_I.sdp" % kwargs["port"]):
            proc = subprocess.Popen(['yes'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.pid:
                RedisStore().persist_data(value=kwargs["port"], key=proc.pid)
                return proc.pid
        return 0
    except Exception as e:
        print(e)
        return 0


def write_sdp_file(port, sdp_content):
    """
    Create the sdp file.

    @param port: used to name the sdp file
    @param content: the content needs to be stored on file
    """
    try:
        with open("sdps/%s_I.sdp" % port, "wb") as input:
            input.write(bytes(sdp_content, 'UTF-8'))
        return 1
    except Exception as e:
        print(e)
        return 0


def stop_stream_and_delete_file(pid):
    """
    Kill the streaming process, looking for the <pid>;
    remove the sdp file looking for its port in Redist Store

    @param pid: the PID belonging to process needs to be killed
    """
    try:
        port = RedisStore().read_data(key=pid)
        if os.path.isfile("sdps/%s_I.sdp" %port.decode(encoding='UTF-8')):
            os.kill(pid, signal.SIGKILL)
            os.remove("sdps/%s_I.sdp" %port.decode(encoding='UTF-8'))
            RedisStore().delete_data(key=pid)
            return 1
        return 0
    except Exception as e:
        print(e)
        return 0


def get_current_streams():
    """
    Get current streams
    """
    return list(map(lambda item: item.decode("UTF-8"), RedisStore().get_current_streams(key=None)))
    

def auth_request(request):
    """
    Function acts as a decorator to check if HTTP requests comes from localhost.

    @param: the parsed HTTP request, created by the Bottle Framework
    """
    def auth_request(controller):
        def check_remote_addr():

            remote_addr = request.remote_addr
            if remote_addr == "127.0.0.1":
                return controller()
            abort(403, "Forbidden")
        return check_remote_addr
    return auth_request


def singleton(cls):
    """Keeps trace of created objects, returning them when needed
    It acts as a singleton helper function.

    @param cls: the class needs to be instantiated
    """
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class RedisStore(object):
    """
    Map getting and setting procedures to Redis store and keeps trace of connection.
    """
    def __init__(self):
        """
        Create the class, along with some partial implemeneted methods, for setting and getting data.
        """
        self.connection = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.persist_data = functools.partial(self.__redis_service, function=self.connection.set)
        self.read_data = functools.partial(self.__redis_service, function=self.connection.get)
        self.delete_data = functools.partial(self.__redis_service, function=self.connection.delete)
        self.get_current_streams = functools.partial(self.__redis_service, function=self.connection.keys)

    def __redis_service(self, key, function, value=None):
        """
        High order function to set/get content to Redis.
        """
        if not key:
            return function()
        if value:
            return function(key, value)
        return function(key)
