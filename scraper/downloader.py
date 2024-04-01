import os
import threading
import concurrent.futures
import requests.exceptions
import urllib.request
from tqdm import tqdm

def _download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'})
    filename = os.path.join(path, url.split('/')[-1])
    with urllib.request.urlopen(req) as response, open(filename, 'wb') as output:
        data = response.read()
        output.write(data)

class Downloader:

    def downloadUrls(self, path, urls):
        os.makedirs(path, exist_ok=True)

        total = len(urls)
        lock = threading.Lock()

        def update_progress():
            with lock:
                pbar.update(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            with tqdm(total=total) as pbar:
                futures = []
                for url in urls:
                    try:
                        future = executor.submit(_download, url, path)
                        future.add_done_callback(lambda _: update_progress())
                        futures.append(future)
                    except requests.exceptions.RequestException as e:
                        print(f"Error! {e}")

                for future in concurrent.futures.as_completed(futures):
                    future.result()

    
