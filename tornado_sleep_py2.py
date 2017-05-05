import time
from tornado.ioloop import IOLoop
from tornado import    gen

@gen.coroutine
def task():
    raise gen.Return( gen.sleep(8))


@gen.coroutine
def main():
    raise gen.Return(gen.Task(
        gen.sleep
    ))

if __name__ == "__main__":
    loop = IOLoop.instance()
    loop.run_sync(main)