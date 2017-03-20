import unittest

from jsonrpc2_base.header_factory import HeaderFactory


class HeaderFactoryTest(unittest.TestCase):
    def test(self):
        headerFactory = HeaderFactory()

        dictHeaders1 = headerFactory.create("testusername", "testpassword", "application/json")
        self.assertEquals("Basic dGVzdHVzZXJuYW1lOnRlc3RwYXNzd29yZA==", dictHeaders1.get("Authorization"))
        self.assertEquals("application/json", dictHeaders1.get("Content-Type"))

        dictHeaders2 = headerFactory.create("alabalaportocala", "anaaremere", "application/xml")
        self.assertEquals("Basic YWxhYmFsYXBvcnRvY2FsYTphbmFhcmVtZXJl", dictHeaders2.get("Authorization"))
        self.assertEquals("application/xml", dictHeaders2.get("Content-Type"))
