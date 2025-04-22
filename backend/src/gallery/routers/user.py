from ..models.tables import User
from ..schemas import user as user_schema
from . import base
from .. import types


class UserRouter(base.Router):

    _PREFIX = '/user'
    _TAGS = ['User']

    def _set_routes(self):

        @self.router.get("/{user_id}", response_model=user_schema.UserPublic)
        async def get_user_by_id(user_id: types.User.id):
            async with self.client.AsyncSession() as session:
                return user_schema.UserPublic(id=user_id, username='test')
