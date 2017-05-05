from ashmolean import *


def run_subtask(ids):

    local_executor = ThreadPoolExecutor(10)
    bytes_data = [local_executor.submit(image_data_from_id, image_id) for image_id in ids]
    # no point in using threads here, just do it synchronously
    data = []
    for image_bytes in as_completed(bytes_data):
        data.append(process_image_bytes(image_bytes.result()) )

    return data





class RequestHandler():
    def __init__(self, counter, client, url, completed):
        self.client = client
        self.counter = counter
        self.url = url
        self.completed = completed

    @gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient(io_loop=self.client.loop)
        http_client.configure(None, defaults=dict(
            connect_timeout=3600, request_timeout=3600, validate_cert=False))
        while True:
            if self.counter.count < 10:

                self.counter.count += 1
                resp = yield http_client.fetch(self.url)
                self.counter.count = self.counter.count - 1
                distributed_future = self.client.submit(process_image_bytes, resp.body)
                self.completed.append(distributed_future)

                break
            else:
                yield gen.sleep(0.01)



class Counter():
    def __init__(self):
        self.count = 0



def run_on_cluster():
    # create a cluster with 10 threads per worker
    start = time.time()
    with worker_client() as wc:
        df = get_data()[:100]

        images = df["id"]
        # get back some futures
        completed = []

        counter = Counter()
        for image_id in images:
            image_url = IMAGE_URL.format(image_id)
            rh = RequestHandler(counter, wc, image_url, completed)
            wc.loop.add_callback(rh.get)

        while True:

            time.sleep(0.001)
            if len(completed) == len(images):
                future = wc.submit(get_tsne, df, completed)
                future.result()
                break
            else:
                pass
                #print(len(completed))
    print("Took {} seconds".format(time.time() - start))
    return "done"
    # run the t-SNE analysis


def run():
    # create a cluster with 10 threads per worker
    client = Client()
    future = client.submit(run_on_cluster)
    future.result()

if __name__ == '__main__':
    run()