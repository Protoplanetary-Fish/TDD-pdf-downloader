from pathlib import Path
from download_manager import DownloadManager
from timing import start_timer, end_timer


if __name__ == "__main__":
    start = start_timer()

    excel_path = Path("data/in/GRI_2017_2020.xlsx")
    output_dir = Path("data/out")

    manager = DownloadManager(excel_path=excel_path, output_dir=output_dir, num_new_files=20)

    manager.run()
    end_timer(start)