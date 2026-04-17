# Foreign imports
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
# Custom imports
from pdf_downloader import PDFDownloader
from blacklist      import Blacklist
from data_parser    import ExcelReader

class DownloadManager:
    """
    Fetches all URLs from an excel-file.
    Downloads max_workers .pdf files at once until either num_new_files is reached or there are no more URLs in the provided excel file.
    Files are saved as their BRnum number (a column named BRnum in the excel file).

    Skips files already downloaded and uses a blacklist to store unresponsive URLs and hosts.
    """
    def __init__(self, excel_path: Path, output_dir: Path, num_new_files=10, max_workers=15):
        self.excel_reader = ExcelReader(excel_path)
        self.output_dir = output_dir
        self.blacklist = Blacklist()
        self.num_new_files = num_new_files
        self.max_workers = max_workers
        self.downloader = PDFDownloader(output_dir=output_dir, blacklist=self.blacklist)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    ## Reads BRnum and groups URLs by the BRnum line they're on
    def _group_urls(self):
        brnum_map = {}
        for url, brnum in self.excel_reader.get_valid_urls():
            brnum_map.setdefault(brnum, []).append(url)
        return {k: list(set(v)) for k, v in brnum_map.items()}
    
    ## Runs the download script
    def run(self):
        brnum_map = self._group_urls()
        new_files_count = 0
        processed_brnums = set()

        # Process BRnums incrementally
        remaining_brnums = list(brnum_map.keys())
        while remaining_brnums and new_files_count < self.num_new_files:
            # Get the batch to be submitted
            batch = remaining_brnums[:self.max_workers]
            # Removes the batch from list of remaining
            remaining_brnums = remaining_brnums[self.max_workers:]

            # Parallel processing of downloads
            futures = {}
            with ThreadPoolExecutor(max_workers=len(batch)) as executor:
                # Dispatch download_brnum() for each worker
                for i, brnum in enumerate(batch):
                    future = executor.submit(
                        self.downloader.download_brnum,
                        brnum,
                        brnum_map[brnum],
                        new_files_count,
                        self.num_new_files
                    )
                    futures[future] = brnum
                    processed_brnums.add(brnum)
                
                # Fetch results from dispatches
                # Result is a string that informs us how the download went
                for future in as_completed(futures):
                    brnum = futures[future]
                    try:
                        result = future.result(timeout=30)
                    except Exception as e:
                        print(f"Error processing {brnum}: {e}")
                        continue

                    if result:
                        print(result)
                        if "ALREADY EXISTS" in result:
                            pass
                        elif "OK" in result:
                            new_files_count += 1

                    # Early out if the number of new files has been achieved
                    if new_files_count >= self.num_new_files:
                        break

            if new_files_count >= self.num_new_files:
                break
        
        print(f"\nFinished: {new_files_count}/{self.num_new_files} new files downloaded")