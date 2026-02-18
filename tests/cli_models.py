from pydantic import AnyUrl, BaseModel


class CliModel(BaseModel):
    name: str
    source: AnyUrl
