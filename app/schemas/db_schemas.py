from pydantic import BaseModel


class ColumnSchema(BaseModel):
    name: str
    description: str
    possible_values: list[str] | None
    data_type: str


class TableSchema(BaseModel):
    name: str
    description: str
    columns: list[ColumnSchema]


class DatabaseSchema(BaseModel):
    # name: str
    # description: str
    tables: list[TableSchema]
