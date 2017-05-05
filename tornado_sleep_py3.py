import time
from tornado.ioloop import IOLoop
from tornado import    gen

@gen.coroutine
def task():
    yield gen.sleep(8)


@gen.coroutine
def main():
    yield [task() for i in range(0,3600)]

if __name__ == "__main__":
    loop = IOLoop.instance()
    loop.run_sync(main)