import pytest
from pydantic import ValidationError

from richforms.example import Family, Person


def test_person_model_accepts_example_payload() -> None:
    person = Person.model_validate(
        {
            "name": "Ada Lovelace",
            "age": 36,
            "email": "ada@example.com",
            "hobbies": ["math", "poetry"],
        }
    )

    assert person.name == "Ada Lovelace"
    assert person.age == 36


def test_family_requires_one_or_more_persons() -> None:
    with pytest.raises(ValidationError):
        Family.model_validate({"family_name": "Lovelace", "persons": []})
