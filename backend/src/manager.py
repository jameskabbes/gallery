import asyncio
import typing
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from gallery import models
# Adjust the import as necessary
from main import login, c, post_user

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
    # c.create_tables()

    # user = models.UserCreate(
    #     username="admin", email="test@test.com", password="password")
    # await post_user(user)

    with Session(c.db_engine) as session:

        # gallery = models.Gallery(
        #     id='1', name='Test Gallery')
        # gallery.add_to_db(session)

        gallery = models.Gallery.get_by_id(session, '1')
        print(gallery)

        # perm = models.GalleryPermission(
        #     gallery_id='1', user_id='2', permission_level=models.PermissionLevel.EDITOR)

        # perm.add_to_db(session)

        # print(models.GalleryPermission.get_by_id(session, ('1', '1')))

        # gallery = models.Gallery.get_by_id(session, '1')
        # print(gallery)

        # form_data = mock_depends(OAuth2PasswordRequestForm)
        # token_response = await login(form_data)
        # print(token_response)

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
