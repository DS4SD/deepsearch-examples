import glob
import os
import uuid
from pathlib import Path
from typing import Optional, Set

import deepsearch as ds
import nbformat
from deepsearch.cps.client.components.elastic import ElasticProjectDataCollectionSource
from nbclient.exceptions import CellTimeoutError
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text

from dsnotebooks.settings import ProjectNotebookSettings
from nbrunner.settings import NotebookRunnerSettings


class NotebookRunner:
    def __init__(self, settings: Optional[NotebookRunnerSettings] = None):
        _settings = settings or NotebookRunnerSettings()
        # print(f"{_settings=}")

        self.run_id = uuid.uuid4().hex
        print(f"{self.run_id=}")

        self.output_dir_path = Path(_settings.output_root_dir) / self.run_id
        self.output_dir_path.mkdir(parents=True, exist_ok=True)

        nb_settings = ProjectNotebookSettings()
        self.api = ds.CpsApi.from_env(profile_name=nb_settings.profile)
        self.proj_key = nb_settings.proj_key

        excl_paths = {Path(f).resolve() for f in _settings.excluded}
        # print(f"{excl_paths=}")

        glob_iter = glob.iglob(_settings.input_root_dir + "/**/*.ipynb", recursive=True)
        self.paths = sorted(
            [p for f in glob_iter if (p := Path(f)).resolve() not in excl_paths],
            key=str,
        )
        # print(f"{self.paths=}")

        self.short_id_len = _settings.short_id_len

    def execute_notebook(self, run_id, notebook_path):

        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

        output_filename = (
            self.output_dir_path / f"{Path(notebook_path.name).stem}_{run_id}.ipynb"
        )
        try:
            out = ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        except (CellExecutionError, CellTimeoutError) as e:
            print(f"=> Error during {run_id}; check {output_filename} for details")
            print(e.traceback)
            out = None
        finally:
            with open(output_filename, mode="w", encoding="utf-8") as f:
                nbformat.write(nb, f)
        return out

    def print_summary_table(self, err_pos: Set[int]):
        table = Table(title="Summary", show_lines=True)
        table.add_column("#")
        table.add_column("Notebook", overflow="fold")
        table.add_column("Status")
        ok_txt = Text("OK", style=Style(color="green"))
        err_txt = Text("ERROR", style=Style(color="red"))
        for i, notebook_path in enumerate(self.paths):
            table.add_row(
                str(i + 1), str(notebook_path), ok_txt if i not in err_pos else err_txt
            )

        console = Console(force_terminal=True)
        console.print(table)

    def cleanup_index_by_name(self, proj_key: str, idx_name: str):
        indices = self.api.data_indices.list(proj_key=proj_key)
        for idx in indices:
            if idx.name == idx_name:
                print(
                    f'Deleting index (name="{idx.name}", key="{idx.source.index_key}"'
                )
                self.api.data_indices.delete(
                    coords=ElasticProjectDataCollectionSource(
                        proj_key=proj_key,
                        index_key=idx.source.index_key,
                    ),
                )

    def run(self):

        err_pos = set()  # positions of errors
        for i, notebook_path in enumerate(self.paths):
            run_item_id = uuid.uuid4().hex
            print(f"[{i+1}/{len(self.paths)}] Running {str(notebook_path)}")
            new_idx_name = (
                f"{self.run_id[:self.short_id_len]}_{run_item_id[:self.short_id_len]}"
            )
            os.environ["DS_NB_NEW_IDX_NAME"] = new_idx_name
            res = self.execute_notebook(
                run_id=run_item_id,
                notebook_path=notebook_path,
            )
            if res is None:
                err_pos.add(i)

            self.cleanup_index_by_name(proj_key=self.proj_key, idx_name=new_idx_name)

        print(80 * "-")
        self.print_summary_table(err_pos=err_pos)
        print(80 * "-")

        n_total = len(self.paths)
        n_err = len(err_pos)
        n_success = n_total - n_err
        print(f"Successful runs: {n_success}/{n_total}")
        print()

        exit(code=0 if n_err == 0 else 1)


if __name__ == "__main__":
    runner = NotebookRunner()
    runner.run()
