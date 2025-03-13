from gallery import models
from gallery.client import Client
import asyncio

c = Client()


async def main():
    async with c.AsyncSession() as session:
        # users = session.query(models.UserDB).all()
        new_user: models.UserDB = await models.User.api_post(session=session, c=c, authorized_user_id=None, admin=False,
                                                             create_model=models.UserAdminCreate(email=input('email: '), user_role_id=1))

        input('press enter')
        await models.User.api_patch(session=session, c=c, id=new_user._id, update_model=models.UserAdminUpdate(phone_number='1231231233'), admin=True)

        input('press enter')

        await models.User.api_delete(session=session, c=c, id=new_user._id, admin=True)


if __name__ == '__main__':
    asyncio.run(main())
