from pydantic import BaseModel, EmailStr, constr, field_validator


class UserCreateValidator(BaseModel):
    username: constr(min_length=3, max_length=20)
    email: EmailStr
    password: constr(min_length=8)

    @field_validator("username")
    def validate_username(self, value):
        if not value.isalnum():
            raise ValueError("Username must contain only alphanumeric characters")
        return value

    @field_validator("password")
    def validate_password(self, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value
