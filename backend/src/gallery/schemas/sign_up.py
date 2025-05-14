from sqlmodel import Field
from pydantic import BaseModel
from src.gallery import types


class SignUpAdminCreate(BaseModel):
    email: types.SignUp.email
    expiry: types.AuthCredential.expiry
