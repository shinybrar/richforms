from pydantic import AnyUrl, BaseModel, Field


class Person(BaseModel):
    name: str = Field(..., description="Full name.", examples=["Ada Lovelace"])
    age: int = Field(..., ge=0, description="Age in years.", examples=[36])
    email: str = Field(
        ...,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="Primary contact email.",
        examples=["ada@example.com"],
    )
    hobbies: list[str] = Field(
        default_factory=list,
        description="Optional hobbies.",
        examples=[["math", "poetry"]],
    )


class Family(BaseModel):
    family_name: str = Field(..., description="Family surname.", examples=["Lovelace"])
    persons: list[Person] = Field(
        ...,
        min_length=1,
        description="One or more family members.",
        examples=[
            [
                {
                    "name": "Ada Lovelace",
                    "age": 36,
                    "email": "ada@example.com",
                    "hobbies": ["math", "poetry"],
                }
            ]
        ],
    )


class Metadata(BaseModel):
    name: str = Field(
        ...,
        title="Name",
        description="Name of the project.",
        examples=["richforms"],
    )
    repository: AnyUrl = Field(
        ...,
        title="Repository",
        description="Repository URL",
        examples=["https://github.com/shinybrar/richforms"],
    )
    license: str = Field("MIT", title="License", description="SPDX license")
    version: str = Field(
        ...,
        title="Version",
        description="Version of the project.",
        examples=["0.1.0"],
    )
