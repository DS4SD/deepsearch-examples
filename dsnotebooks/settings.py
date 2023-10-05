from pydantic import BaseSettings, validator
from dotenv import find_dotenv

class NotebookSettings(BaseSettings):
    class Config:
        env_prefix = "DS_NTBK_"
        env_file = find_dotenv()
        env_file_encoding = "utf-8"

    profile: str = "sds"


class ProjectNotebookSettings(NotebookSettings):
    proj_key: str = ""
    cleanup: bool = True

    @validator("proj_key")
    def set_proj_key(cls, v):
        return v or input("Project key: ")
