from pydantic import BaseModel, constr, field_validator


class MoveValidator(BaseModel):
    move: constr(min_length=2, max_length=5)

    @field_validator("move")
    def validate_move_format(cls, value):
        if not value[0].isalpha() or not value[1:].isdigit():
            raise ValueError("Move must start with a letter followed by a number, e.g., 'e2'")
        return value