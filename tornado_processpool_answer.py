TTF_URL = "http://tutorial.zegami.net.s3.eu-west-2.amazonaws.com/ashmolean/data.tab"

IMAGE_URL = "http://tutorial.zegami.net.s3.eu-west-2.amazonaws.com/ashmolean/{}.jpg"

# TSNE on images
import os
import io
import requests
import time
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from distributed.client import Client,   wait
from distributed import worker_client, LocalCluster
from concurrent.futures import ThreadPoolExecutor, as_completed
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
output_file = "zegami_tsne.tab"

# setup a standard image size; this will distort some images but will get everything into the same shape
STANDARD_SIZE = (100, 100)


def img_data_to_matrix(image_data, verbose=False):
    """
    takes a filename and turns it into a numpy array of RGB pixels
    """

    bio = io.BytesIO(image_data)
    bio.seek(0)
    img = Image.open(bio)
    img = img.resize(STANDARD_SIZE)
    img = list(img.getdata())
    img = np.array(img)

    return img


def flatten_image(img):
    """
    takes in an (m, n) numpy array and flattens it
    into an array of shape (1, m * n)
    """
    s = img.shape[0] * img.shape[1]
    img_wide = img.reshape(1, s)
    return img_wide[0]


def get_data():
    resp = requests.get(TTF_URL, stream=True)
    data = pd.read_csv(io.StringIO(resp.content.decode("latin-1")),
                       sep="\t",
                       header=0)
    return data.dropna(subset=["id"])


def get_pca(data):
    pca = TSNE()

    X = pca.fit_transform(data)
    results = pd.DataFrame({"x": X[:, 0], "y": X[:, 1]})
    return results


def image_data_from_id(image_id):
    if str(image_id) == "nan":
        raise Exception("ID should not be nan")
    image_url = IMAGE_URL.format(image_id)
    image_data = requests.get(image_url, timeout=60).content
    return image_data


def process_image_bytes(image_bytes):
    matrix = img_data_to_matrix(image_bytes)
    return flatten_image(matrix)





def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_tsne(df, data):
    results = get_pca(data)
    df['x'] = results['x']
    df['y'] = results['y']
    print("==========================")
    # print str(df)
    print("Appended x and y coordinates and created " + output_file + ".")
    df.to_csv(output_file, sep="\t", index=False)
    print("==========================")


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