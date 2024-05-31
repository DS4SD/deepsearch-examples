from datetime import datetime
from typing import Optional

from dotenv import find_dotenv
from pydantic.v1 import BaseSettings, validator


class NotebookSettings(BaseSettings):
    class Config:
        env_prefix = "DS_NB_"
        env_file = find_dotenv()
        env_file_encoding = "utf-8"

    profile: Optional[str] = None  # defaulting to the active profile


class ProjectNotebookSettings(NotebookSettings):
    proj_key: str = ""
    new_idx_name: str = f"tmp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cleanup: bool = True

    @validator("proj_key")
    def set_proj_key(cls, v):
        return v or input("Project key: ")


class KGProjectNotebookSettings(ProjectNotebookSettings):
    kg_key: str = ""

    @validator("kg_key")
    def set_kg_key(cls, v):
        return v or input("Knowledge graph key: ")


class CollOptionalNotebookSettings(NotebookSettings):
    proj_key: Optional[str] = None
    index_key: Optional[str] = None
