from tornado import ioloop, gen, httpclient
import json
import motor

class DataReciever(object):
    def __init__(self):
        self.partial_data = None
        self.partial_chars = None
        self.client = motor.motor_tornado.MotorClient()
        self.db = self.client['test_database']

    # def data_from_line(self, line):
    def my_callback(self, result, error):
        print('result %s' % repr(result.inserted_id))

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
                    self.db.test_collection.insert_one(data, callback=self.my_callback)
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