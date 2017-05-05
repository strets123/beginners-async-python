from tornado import ioloop, gen, httpclient
import json

class DataReciever(object):
    def __init__(self):
        self.partial_data = None

    # def data_from_line(self, line):

    def streaming_callback(self, input):
        data = input.decode("utf-8")
        lines = data.splitlines()
        for line in lines:
            if self.partial_data is not None:
                line = self.partial_data + line
                self.partial_data = None
            if len(line) > 0  and len(line) < 100 and "data:".startswith(line[:4]):
                self.partial_data = line
            if line.startswith("data:"):
                try:
                    data = json.loads(line[5:])
                    print(data)
                except (ValueError, IndexError):
                    self.partial_data = line






@gen.coroutine
def main():
    http_client = httpclient.AsyncHTTPClient()
    dr = DataReciever()
    yield http_client.fetch(
        'https://stream.wikimedia.org/v2/stream/recentchange',
        streaming_callback=dr.streaming_callback,
        request_timeout=3600
    )


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main)