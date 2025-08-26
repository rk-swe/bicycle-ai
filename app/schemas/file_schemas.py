from dataclasses import dataclass
from typing import Self

from app.services import utils


@dataclass
class InputFile:
    folder_name: str
    file_name: str
    file_ext: str

    @property
    def file_name_with_ext(self: Self) -> str:
        return f"{self.file_name}.{self.file_ext}"

    @property
    def file_path(self: Self) -> str:
        return f"{self.file_name}.{self.file_ext}"

    @property
    def sql_table_name(self: Self) -> str:
        return f"{utils.to_snake_case(self.file_name)}.{self.file_ext}"
