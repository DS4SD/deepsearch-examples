from typing import List
from pydantic import BaseSettings
from dotenv import find_dotenv

class NotebookRunnerSettings(BaseSettings):
    class Config:
        env_prefix = "DS_NR_"
        env_file = find_dotenv()
        env_file_encoding = "utf-8"

    input_root_dir: str = "./examples"
    output_root_dir: str = ".local/nb_runner"
    excluded: List[str] = []  # excluded notebooks

    short_id_len: int = 7
