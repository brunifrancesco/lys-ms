from bottle import Bottle
from bottle import run
from bottle import request
from bottle import response
from utils import auth_request
from utils import stop_stream_and_delete_file
from utils import write_sdp_file
from utils import start_stream_and_store
from utils import get_current_streams


app = Bottle()


def result(status, result_dict):
    response.status = status
    return result_dict


@app.post('/recordStream')
@auth_request(request)
def recor_stream():
    """
    Record stream API; start a background process, given sdp file and port
    """
    if "port" in request.json and "filename" in request.json:
        res = start_stream_and_store(**request.json)
        if res:
            return dict(details="Ok", pid=res)
        return result(404, dict(details="Resource does not exists"))
    return result(400, dict(details="Missing port/filename param"))


@app.post('/writeSdp')
@auth_request(request)
def write_sdp():
    """
    Create the SDP file, whose content comes from client application
    """
    if "port" in request.json and "sdp_content" in request.json:
        if write_sdp_file(**request.json):
            return dict(details="Ok")
        return result(500, dict(details="Unexpected error"))
    return result(400, dict(details="Missing port/sd_content param"))


@app.delete('/writeSdp')
@auth_request(request)
def delete_sdp():
    """
    Delete SDP file and kill process
    """
    if "pid" in request.json:
        res = stop_stream_and_delete_file(request.json["pid"])
        if res:
            return dict(details="Ok")

        return result(500, dict(details="Unexpected error"))
    else:
        return result(400, dict(details="Missing pid param"))


@app.get('/currentStreams')
@auth_request(request)
def get_current_stream():
    """
    Get current streams
    """
    return dict(data=get_current_streams())

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True, app=app)
