from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_downloader import PDFDownloader
from blacklist import Blacklist
from data_parser import ExcelReader

class DownloadManager:
    def __init__(self, excel_path: Path, output_dir: Path, num_new_files=10, max_workers=15):
        self.reader = ExcelReader(excel_path)
        self.output_dir = output_dir
        self.blacklist = Blacklist()
        self.num_new_files = num_new_files
        self.max_workers = max_workers
        self.downloader = PDFDownloader(output_dir=output_dir, blacklist=self.blacklist)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _group_urls(self):
        brnum_map = {}
        for url, brnum in self.reader.get_valid_urls():
            brnum_map.setdefault(brnum, []).append(url)
        return {k: list(set(v)) for k, v in brnum_map.items()}

    def run(self):
        brnum_map = self._group_urls()
        new_files_count = 0
        processed_brnums = set()
        lock = Lock()

        # Process BRnums incrementally to respect the num_new_files limit
        remaining_brnums = list(brnum_map.keys())
        while remaining_brnums and new_files_count < self.num_new_files:
            # Submit at most max_workers tasks at a time
            batch = remaining_brnums[:self.max_workers]
            remaining_brnums = remaining_brnums[self.max_workers:]

            futures = {}
            with ThreadPoolExecutor(max_workers=len(batch)) as executor:
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

                    # Stop early if we reached the target
                    if new_files_count >= self.num_new_files:
                        break

            if new_files_count >= self.num_new_files:
                break
        
        print(f"\nFinished: {new_files_count}/{self.num_new_files} new files downloaded")