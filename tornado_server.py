import asyncio

import time
import tornado
import tornado.netutil
import tornado.process
from tornado.httpserver import HTTPServer
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.web import Application
from tornado import concurrent
from tornado.concurrent import run_on_executor


# executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        time.sleep(1)
        self.write("Hello, world %s" % time.time())


class SleepHandler(tornado.web.RequestHandler):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    # @run_on_executor
    def sleep_time(self, n):
        start_time = time.time()
        time.sleep(n)
        print("Time to wake! %s" % (time.time() - start_time))

    # @asyncio.coroutine
    def get(self, n):
        # Start the background operations
        # Working :D
        # start_time = time.time()
        # blocking_tasks = [asyncio.get_event_loop().run_in_executor(executor, time.sleep, float(n))]

        asyncio.get_event_loop().run_in_executor(self.executor, self.sleep_time, float(n))

        # fut = self.executor.submit(self.sleep_time, float(n))
        # await asyncio.wrap_future(fut)

        # for future in asyncio.as_completed(blocking_tasks):
        #     try:
        #         # result = await future
        #         completed, pending = await asyncio.wait(blocking_tasks)
        #         results = [t.result() for t in completed]
        #
        #         self.write("Time to wake! %s" % (time.time() - start_time))
        #         self.finish()
        #     except Exception as e:
        #         print(e)

        # Not Working
        # futures = [executor.submit(time.sleep, float(n))]
        # for future in concurrent.futures.as_completed(futures):
        #     try:
        #         future.result()
        #     except Exception as e:
        #         print(e)

        # def on_complete(self, res):
        #     self.write("{}".format(res))
        #     self.finish()


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
        (r"/sleep/(\d+)", SleepHandler),
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
