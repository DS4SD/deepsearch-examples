from datetime import datetime
from typing import Optional

from deepsearch.cps.queries import ConstrainedWeight
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


class CollQANotebookSettings(ProjectNotebookSettings):
    sem_on_idx_key: str
    retr_k: int = 5
    text_weight: ConstrainedWeight = 0.1
    rerank: bool = False
    skip_ingested_docs: bool = True
    raise_on_sem_err: bool = True


class DocQANotebookSettings(CollQANotebookSettings):
    sem_on_idx_doc_hash: str
    sem_off_idx_key: str
    sem_off_idx_doc_hash: str
