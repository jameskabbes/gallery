from gallery import models
from gallery.client import Client
import asyncio


async def main():
    c = Client()

    async with c.AsyncSession() as session:
        # users = session.query(models.UserDB).all()
        new_user = await models.User.api_post(session=session, c=c, create_model=models.UserAdminCreate(email=input('email: '), user_role_id=1))

        new_user = await models.User.api_post2(session=session, c=c, create_model=models.UserAdminCreate(email=input('email: '), user_role_id=1))

        input('press enter')
        await models.User.api_patch(session=session, c=c, id=new_user._id, update_model=models.UserAdminUpdate(phone_number='1231231233'), admin=True)

        input('press enter')

        c = await models.TableService.api_get(session, c=c)

        b = await models.User.api_get(session=session, c=c, id=new_user._id, admin=True)
        print(b.__dict__)

        input('press enter')

        await models.User.api_delete(session=session, c=c, id=new_user._id, admin=True)

        f = await models.User.api_post_wrapper(models.User.api_post2)
        g = await f(models.User)

if __name__ == '__main__':
    asyncio.run(main())
