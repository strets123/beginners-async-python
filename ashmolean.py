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
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
output_file = "zegami_tsne.tab"

# setup a standard image size; this will distort some images but will get everything into the same shape
STANDARD_SIZE = (100, 100)


def img_data_to_matrix(image_data, verbose=False):
    """
    takes a jpeg or oher image bytes object and turns it into a numpy array of RGB pixels
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
    """
    Requests the CSV data over the web and returns it as a cleaned pandas dataframe
    """
    resp = requests.get(TTF_URL, stream=True)
    data = pd.read_csv(io.StringIO(resp.content.decode("latin-1")),
                       sep="\t",
                       header=0)
    return data.dropna(subset=["id"])


def get_pca(data):
    """
    Runs the TSNE algorithm over a set of image data
    """
    pca = TSNE()

    X = pca.fit_transform(data)
    results = pd.DataFrame({"x": X[:, 0], "y": X[:, 1]})
    return results


def image_data_from_id(image_id):
    """
    Take the image id and return the bytes content of the image via an http request
    """
    if str(image_id) == "nan":
        raise Exception("ID should not be nan")
    image_url = IMAGE_URL.format(image_id)
    image_data = requests.get(image_url, timeout=60).content
    return image_data


def process_image_bytes(image_bytes):
    """
    Reshape the image pixels into a flat list of tuples of pixel values. The list should be of equla size for all images
    """
    matrix = img_data_to_matrix(image_bytes)
    return flatten_image(matrix)





def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_tsne(df, data):
    """
    Given a flat list of tuples of pixel values write out the TSNE CSV output file
    """
    results = get_pca(data)
    df['x'] = results['x']
    df['y'] = results['y']
    print("==========================")
    # print str(df)
    print("Appended x and y coordinates and created " + output_file + ".")
    df.to_csv(output_file, sep="\t", index=False)
    print("==========================")

def run():
    """
    main script runner for the synchronous version of this ashmolean data processing script
    """
    df = get_data()
    images = df["id"]
    data = []
    labels = []
    bytes_data = [image_data_from_id(image_id) for image_id in images]
    data = [process_image_bytes(image_bytes) for image_bytes in bytes_data]

    #pca = TSNE()
    # or can do PCA
    get_tsne(df, data)

run()
