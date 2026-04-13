from pathlib import Path
from download_manager import DownloadManager

if __name__ == "__main__":
    excel_path = Path("data/in/GRI_2017_2020.xlsx")
    output_dir = Path("data/out")

    manager = DownloadManager(excel_path=excel_path, output_dir=output_dir, num_new_files=50)
    manager.run()