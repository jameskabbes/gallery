from ..models.tables import user
from . import base
from .. import types


class UserRouter(base.Router):

    _PREFIX = '/user'
    _TAGS = ['User']

    def _set_routes(self):

        @self.router.get("/{user_id}", response_model=user.UserPublic)
        async def get_user_by_id(user_id: types.User.id):
            async with self.client.AsyncSession() as session:
                return user.UserPublic(id=user_id, username='test')
