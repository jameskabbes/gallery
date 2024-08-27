import asyncio
import typing
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
# Adjust the import as necessary
from main import login

# Mock the OAuth2PasswordRequestForm


class MockOAuth2PasswordRequestForm:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

# Mock the Depends function


def mock_depends(dependency):
    if dependency == OAuth2PasswordRequestForm:
        return MockOAuth2PasswordRequestForm(username="admin", password="password")

# Call the function directly


async def main():
    form_data = mock_depends(OAuth2PasswordRequestForm)
    token_response = await login(form_data)
    print(token_response)

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
