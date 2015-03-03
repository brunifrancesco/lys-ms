from webtest import TestApp
import ms
import unittest
import os

from utils import RedisStore

application = TestApp(ms.app, extra_environ=dict(REMOTE_ADDR='127.0.0.1'))


class TestWriteSDP(unittest.TestCase):
    def test_write_sdp(self):
        response = application.post_json("/writeSdp", dict(port=10, sdp_content="ciaociaociao"))
        self.assert_(response.status_int == 200)
        self.assert_(os.path.isfile("sdps/10_I.sdp"))


class StreamTest(unittest.TestCase):
    def setUp(self):
        RedisStore().persist_data(key="test", value="test")
        with open("sdps/10_I.sdp", "wb") as input:
            input.write(bytes("Dummy content", 'UTF-8'))

    def tearDown(self):
        for key in RedisStore().connection.keys():
            RedisStore().delete_data(key)

    def test_recor_stream(self):
        respone = application.post_json("/recordStream", dict(port=10, filename="filename_ex"))
        self.assert_(respone.json["pid"] > 1)
        self.assert_(RedisStore().read_data(key=respone.json["pid"]).decode("utf-8") == '10')


        pid = respone.json["pid"]
        response = application.delete_json("/writeSdp", dict(pid=pid))
        self.assert_(response.status_int == 200)
        self.assert_(RedisStore().read_data(pid) == None)

        response = application.post_json("/recordStream", dict(port=9999, filename="filename_ex"), expect_errors=True)
        self.assert_(response.status_int == 404)

    def test_current_stream(self):
        response = application.get("/currentStreams")
        self.assert_(response.json["data"] == ["test"])

    #def test_sec(self):
    #    application = TestApp(ms.app, extra_environ=dict(REMOTE_ADDR='77.3.4.4'))
    #    response = application.post_json("/writeSdp", dict(port=10, sdp_content="ciaociaociao"))
    #    self.assert_(response.status_int == 403)


if __name__ == "__main__":
    unittest.main()
