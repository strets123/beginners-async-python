from ashmolean import *


def run_subtask(ids):

    local_executor = ThreadPoolExecutor(10)
    bytes_data = [local_executor.submit(image_data_from_id, image_id) for image_id in ids]
    # no point in using threads here, just do it synchronously
    data = []
    for image_bytes in as_completed(bytes_data):
        data.append(process_image_bytes(image_bytes.result()) )

    return data


def run_on_cluster():
    # create a cluster with 10 threads per worker
    start = time.time()
    with worker_client() as wc:
        df = get_data()[:100]

        images =  df["id"]
        # get back some futures
        processed_data = wc.submit(run_subtask, images)


        future = wc.submit(get_tsne, df, processed_data)
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