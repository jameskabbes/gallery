from gallery import models
from gallery.client import Client
import asyncio

c = Client()


async def main():
    with c.Session() as session:
        # users = session.query(models.UserDB).all()
        await models.User.api_post(session=session, c=c, authorized_user_id=None, admin=False,
                                   create_model=models.UserAdminCreate(email='asdf@a.com', user_role_id=1))


if __name__ == '__main__':
    asyncio.run(main())
