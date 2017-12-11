import requests
from gevent import Greenlet
import gevent
from gevent import monkey
import time

# Patch sockets to make requests async and potentially resolve broken pipe errors
# Patching before application code to ensure all functions that have block call potential are patched
monkey.patch_all()

threads = []


def req_call(id):
    start_time = time.time()
    url = 'http://localhost:8888/sleep2'
    print('Thread #{} {} Finished {}'.format(id, requests.get(url), (time.time() - start_time)))


count = 1
while count < 8:
    print('Thread #{} Started'.format(count))
    thread = Greenlet.spawn(req_call, count)
    threads.append(thread)

    count += + 1

gevent.joinall(threads)