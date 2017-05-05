from tornado import gen, ioloop, web

@web.stream_request_body
class Handler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.write('start<br/>')
        yield self.flush()
        yield gen.sleep(5)
        self.write('finish\n')
        yield self.flush()


application = web.Application([(r'/', Handler)])
application.listen(8889)
ioloop.IOLoop.current().start()
