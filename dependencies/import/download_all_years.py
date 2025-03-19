# def fetch_page(api_url: str, page: int) ->List[Dict]:
#     except Exception as e:logger.info('%s', f'Error fetching page {page}: {e}')


# def worker(api_url: str, page_queue: Queue, result_list: List[Dict], lock:
#     threading.Lock) ->None:
#     while not page_queue.empty():
#         with lock:


# def download_paginated_data(api_url: str, destination_path: str, max_pages:
#     Optional[int]=None) ->List[Dict]:
#     if max_pages is None:
#     for page in range(1, max_pages + 1):
#     for _ in range(min(MAX_WORKERS, page_queue.qsize())):
#         thread = threading.Thread(target=worker, args=(api_url, page_queue,
#             all_data, lock))
#     for thread in threads:


# def save_incrementally(data: List[Dict], destination_path: str) ->None:
#     with open(destination_path, 'w') as f:
#     with open(artifacts_path, 'w') as f:


# def download_all(cfg: DictConfig, overwrite_existing: bool=False) ->None:
#     for key, dataset in cfg.data_import.items():
#         for year, api_url in all_urls.items():
#             if not overwrite_existing and os.path.exists(dest_file
#                 ):logger.info('%s', f'Skipping {dest_file}, exists.')
#                 continuelogger.info('%s',
#                     f'Downloading data for {dataset.name} year {year}...')
