import asyncio

import time
import tornado
import tornado.netutil
import tornado.process
from tornado.httpserver import HTTPServer
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.web import Application
from tornado import concurrent


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        time.sleep(1)
        self.write("Hello, world %s" % time.time())


class BackGroundSleepHandler(tornado.web.RequestHandler):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def sleep_time(self, n):
        start_time = time.time()
        time.sleep(n)
        end_time = time.time() - start_time
        print("Time to wake! %s" % end_time)
        return end_time

    async def get(self):
        print('correct')
        futures = asyncio.get_event_loop().run_in_executor(self.executor, self.sleep_time, 1)

        for response in await asyncio.gather(futures):
            self.write('Time to wake! %s' % response)


class AwaitedSleepHandler(tornado.web.RequestHandler):

    async def sleep_time(self, n):
        start_time = time.time()
        time.sleep(n)
        end_time = time.time() - start_time
        print("Time to wake! %s" % end_time)
        self.write('Time to wake! %s' % end_time)
        self.finish()

    async def get(self):
        print('correct')
        response = await asyncio.ensure_future(self.sleep_time(1))

        return 200


def main():
    """
    Tornado AsyncIO integration needs to fork processes before asyncio event loop gets initiated per process
    http://www.tornadoweb.org/en/stable/asyncio.html
    https://stackoverflow.com/questions/42767635
    """
    sockets = tornado.netutil.bind_sockets(8888)
    tornado.process.fork_processes(1)
    AsyncIOMainLoop().install()

    app = Application(handlers=[
        (r"/", MainHandler),
        (r"/sleep", BackGroundSleepHandler),
        (r"/sleep2", AwaitedSleepHandler),
    ])

    server = HTTPServer(app)

    server.add_sockets(sockets)
    print('Server Started')

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        event_loop.run_until_complete(event_loop.shutdown_asyncgens())
        event_loop.close()


if __name__ == '__main__':
    main()
