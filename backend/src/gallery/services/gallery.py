from sqlmodel import select
from ..models.tables import Gallery as GalleryTable
from . import base
from .. import types

from ..schemas import gallery as gallery_schema


class Gallery(
        base.Service[
            GalleryTable,
            types.Gallery.id,
            gallery_schema.GalleryAdminCreate,
            gallery_schema.GalleryAdminUpdate,
            gallery_schema.GalleryAfterCreateCustomParams,
            base.AfterReadCustomParams,
            base.AfterUpdateCustomParams,
            gallery_schema.GalleryAfterDeleteCustomParams
        ],
        base.SimpleIdModelService[
            GalleryTable,
            types.Gallery.id,
        ],
):

    _MODEL = GalleryTable

    @classmethod
    def model_folder_name(cls, inst: GalleryTable) -> types.Gallery.folder_name:

        if inst.parent_id == None and inst.name == 'root':
            return inst.user_id
        elif inst.date == None:
            return inst.name
        else:
            return inst.date.isoformat() + ' ' + inst.name

    # @classmethod
    # def get_date_and_name_from_folder_name(cls, folder_name: types.Gallery.folder_name) -> tuple[types.Gallery.date | None, types.Gallery.name]:

    #     match = re.match(r'^(\d{4}-\d{2}-\d{2}) (.+)$', folder_name)
    #     if match:
    #         date_str, name = match.groups()
    #         date = datetime_module.date.fromisoformat(date_str)
    #         return (date, name)
    #     else:
    #         return (None, folder_name)

    # async def get_dir(self, session: Session, root: pathlib.Path) -> pathlib.Path:

    #     if self.parent_id is None:
    #         return root / self.folder_name
    #     else:
    #         a = await (await self.read(session, self.parent_id)).get_dir(session, root)
    #         return a / self.folder_name

    # async def get_parents(self, session: Session) -> list[typing.Self]:

    #     if self.parent_id is None:
    #         return []
    #     else:
    #         return (await self.parent.get_parents(session)) + [self.parent]

    # @classmethod
    # async def get_root_gallery(cls, session: Session, user_id: types.Gallery.user_id) -> typing.Self | None:
    #     return session.exec(select(cls).where(cls.user_id == user_id).where(cls.parent_id == None)).one_or_none()

    # @classmethod
    # async def api_get_is_available(cls, session: Session, gallery_available_admin: GalleryAdminGalleryAvailable) -> None:

    #     # raise an exception if the parent gallery does not exist
    #     if gallery_available_admin.parent_id:
    #         if not await cls.read(session, gallery_available_admin.parent_id):
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND, detail='Parent gallery does not exist')

    #     if session.exec(select(cls).where(cls._build_conditions(gallery_available_admin.model_dump()))).one_or_none():
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

    # @classmethod
    # async def _check_authorization_new(cls, params):
    #     if not params.admin:
    #         if params.authorized_user_id != params.create_model.user_id:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post gallery for another user')

    # async def _check_authorization_existing(self, params):

    #     if not params.admin:
    #         if params.authorized_user_id != self.user_id:

    #             if params.method == 'delete':
    #                 raise HTTPException(
    #                     status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

    #             gallery_permission = await GalleryPermission.read(params.session, (params.id, params.authorized_user_id))

    #             # if the gallery is private and user has no access, pretend it doesn't exist
    #             if not gallery_permission and self.visibility_level == config.VISIBILITY_LEVEL_NAME_MAPPING['private']:
    #                 raise self.not_found_exception()

    #             elif params.method == 'get':
    #                 if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['viewer']:
    #                     raise HTTPException(
    #                         status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

    #             elif params.method == 'patch':
    #                 if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['editor']:
    #                     raise HTTPException(
    #                         status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

    # @classmethod
    # async def _check_validation_post(cls, params):
    #     await cls.api_get_is_available(params.session, GalleryAdminGalleryAvailable(**params.create_model.model_dump(include=GalleryAdminGalleryAvailable.model_fields.keys(), exclude_unset=True)))

    # async def _check_validation_patch(self, params):
    #     # take self, overwrite it with the update_model, and see if the combined model is available
    #     await self.api_get_is_available(params.session, GalleryAdminGalleryAvailable(**{
    #         **self.model_dump(include=list(GalleryAdminGalleryAvailable.model_fields.keys())), **params.update_model.model_dump(include=GalleryAdminGalleryAvailable.model_fields.keys(), exclude_unset=True)
    #     }))

    # @classmethod
    # async def create(cls, params):
    #     gallery = cls(
    #         id=cls.generate_id(),
    #         **params.create_model.model_dump()
    #     )

    #     if params.create_method_params == None:
    #         params.create_method_params = GalleryAdminCreateParams()

    #     if params.create_method_params.mkdir:
    #         (await gallery.get_dir(params.session, params.c.galleries_dir)).mkdir()

    #     return gallery

    # async def update(self, params) -> None:

    #     rename_folder = False

    #     # rename the folder
    #     if 'name' in params.update_model.model_fields_set or 'date' in params.update_model.model_fields_set or 'parent_id' in params.update_model.model_fields_set:
    #         rename_folder = True
    #         original_dir = await self.get_dir(
    #             params.session, params.c.galleries_dir)

    #     self.sqlmodelupdate(
    #         params.update_model.model_dump(exclude_unset=True))

    #     if rename_folder:
    #         new_dir = (await self.get_dir(params.session, params.c.galleries_dir)).parent / self.folder_name
    #         original_dir.rename(new_dir)

    # async def delete(self, params) -> None:

    #     if params.delete_method_params == None:
    #         params.delete_method_params = GalleryAdminCreateParams()

    #     if params.delete_method_params.rmtree:
    #         shutil.rmtree((await self.get_dir(params.session, params.c.galleries_dir)))

    # async def sync_with_local(self, session: Session, c: client.Client, dir: pathlib.Path) -> None:

    #     if not dir.exists():
    #         raise HTTPException(status.HTTP_404_NOT_FOUND,
    #                             detail='Directory not found')

    #     if self.folder_name != dir.name:
    #         raise HTTPException(status.HTTP_400_BAD_REQUEST,
    #                             detail='Folder name does not match gallery name')

    #     files: list[pathlib.Path] = []
    #     dirs: list[pathlib.Path] = []
    #     for item in dir.iterdir():
    #         if item.is_dir():
    #             dirs.append(item)
    #         if item.is_file():
    #             files.append(item)

    #     # Add new galleries, remove old ones
    #     local_galleries_by_folder_name = {
    #         item.name: item for item in dirs}
    #     db_galleries_by_folder_name = {
    #         gallery.folder_name: gallery for gallery in self.children}

    #     local_galleries_folder_names = set(
    #         local_galleries_by_folder_name.keys())
    #     db_galleries_folder_names = set(db_galleries_by_folder_name.keys())

    #     toadd = local_galleries_folder_names - db_galleries_folder_names
    #     to_remove = db_galleries_folder_names - local_galleries_folder_names

    #     for folder_name in to_remove:
    #         gallery = db_galleries_by_folder_name[folder_name]
    #         await Gallery.api_delete(session=session, c=c, id=gallery._id, authorized_user_id=self.user_id, admin=False, delete_method_kwargs=GalleryAdminApiDeleteParams(rmtree=False))

    #     for folder_name in toadd:
    #         date, name = self.get_date_and_name_from_folder_name(
    #             folder_name)
    #         new_gallery = await Gallery.api_post(
    #             session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=GalleryAdminCreate(name=name, user_id=self.user_id, visibility_level=self.visibility_level, parent_id=self.id, date=date),
    #             create_method_kwargs=GalleryAdminCreateParams(mkdir=False))

    #     # add new files, remove old ones
    #     local_file_by_names = {
    #         file.name: file for file in files}
    #     db_files_by_names = {
    #         file.name: file for file in self.files}

    #     local_file_names = set(local_file_by_names.keys())
    #     db_file_names = set(db_files_by_names.keys())

    #     toadd = local_file_names - db_file_names
    #     to_remove = db_file_names - local_file_names

    #     for file_name in to_remove:
    #         file = db_files_by_names[file_name]

    #         # if this is the last image tied to that version, delete the version too
    #         if file.suffix in ImageFileMetadataConfig._SUFFIXES:
    #             image_version = await ImageVersion.read(session, file.image_file_metadata.version_id)
    #             if len(image_version.image_file_metadatas) == 1:
    #                 await ImageVersion.api_delete(session=session, c=c, id=image_version.id, authorized_user_id=self.user_id, admin=False)

    #         await File.api_delete(session=session, c=c, id=file.id, authorized_user_id=self.user_id, admin=False, unlink=False)

    #     image_files: list[File] = []

    #     for file_name in toadd:
    #         stem = local_file_by_names[file_name].stem
    #         suffix = ''.join(suffixes) if (
    #             suffixes := local_file_by_names[file_name].suffixes) else None

    #         new_file = await File.api_post(
    #             session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=FileAdminCreate(stem=stem, suffix=suffix, gallery_id=self.id, size=local_file_by_names[file_name].stat().st_size))

    #         # rename the file, just to make sure the suffix is lowercase
    #         local_file_by_names[file_name].rename(
    #             local_file_by_names[file_name].with_name(new_file.name))

    #         if suffix in ImageFileMetadataConfig._SUFFIXES:
    #             image_files.append(new_file)

    #     # loop through files twice, adding the original images first
    #     for original_images in [True, False]:
    #         for image_file in image_files:

    #             base_name, version, scale = ImageFileMetadata.parse_file_stem(
    #                 image_file.stem)

    #             if original_images == (version == None):

    #                 parent_id = None
    #                 if version is not None:
    #                     image_version_og = session.exec(select(ImageVersion).where(ImageVersion.gallery_id == self._id).where(
    #                         ImageVersion.base_name == base_name).where(ImageVersion.version == None)).one_or_none()

    #                     # if an original exists, assume the version wants to link as the parent
    #                     if image_version_og:
    #                         parent_id = image_version_og._id

    #                 image_version_kwargs = {
    #                     'gallery_id': self.id,
    #                     'base_name': base_name if parent_id is None else None,
    #                     'version': version,
    #                     'parent_id': parent_id
    #                 }

    #                 image_version = session.exec(select(ImageVersion).where(
    #                     ImageVersion._build_conditions(image_version_kwargs))).one_or_none()

    #                 # this if the first file of this version
    #                 if not image_version:
    #                     image_version = await ImageVersion.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageVersionAdminCreate(**image_version_kwargs))

    #                 image_file_metadata = await ImageFileMetadata.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageFileMetadataAdminCreate(file_id=image_file.id, version_id=image_version.id, scale=scale))

    #     # recursively sync children
    #     for child in self.children:
    #         await child.sync_with_local(session, c, dir / child.folder_name)


# class Gallery(
#         Table['Gallery', GalleryTypes.id, GalleryAdminCreate, GalleryAdminCreateParams,
#               BaseModel, GalleryGalleryAdminUpdate, GalleryGalleryAdminUpdateParams, GalleryAdminApiDeleteParams, typing.Literal[()]],
#         GalleryGalleryIdBase,
#         table=True):
#     __tablename__ = 'gallery'

#     name: GalleryTypes.name = Field()
#     user_id: GalleryTypes.user_id = Field(
#         index=True, foreign_key=User.__tablename__ + '.' + User.ID_COLS[0], ondelete='CASCADE')

#     visibility_level: GalleryTypes.visibility_level = Field()
#     parent_id: GalleryTypes.parent_id = Field(nullable=True, index=True,
#                                               foreign_key=__tablename__ + '.id', ondelete='CASCADE')
#     description: GalleryTypes.description = Field(nullable=True)
#     date: GalleryTypes.date = Field(nullable=True)

#     user: 'User' = Relationship(back_populates='galleries')
#     parent: typing.Optional['Gallery'] = Relationship(
#         back_populates='children', sa_relationship_kwargs={'remote_side': 'Gallery.id'})
#     children: list['Gallery'] = Relationship(
#         back_populates='parent', cascade_delete=True)
#     gallery_permissions: list['GalleryPermission'] = Relationship(
#         back_populates='gallery', cascade_delete=True)
#     files: list['File'] = Relationship(
#         back_populates='gallery', cascade_delete=True)
#     image_versions: list['ImageVersion'] = Relationship(
#         back_populates='gallery', cascade_delete=True)

#     _ROUTER_TAG: typing.ClassVar[str] = 'Gallery'

#     @property
#     def folder_name(self) -> GalleryTypes.folder_name:
#         if self.parent_id is None and self.name == 'root':
#             return self.user_id
#         if self.date is None:
#             return self.name
#         else:
#             return self.date.isoformat() + ' ' + self.name

#     @classmethod
#     def get_date_and_name_from_folder_name(cls, folder_name: GalleryTypes.folder_name) -> tuple[GalleryTypes.date | None, GalleryTypes.name]:

#         match = re.match(r'^(\d{4}-\d{2}-\d{2}) (.+)$', folder_name)
#         if match:
#             date_str, name = match.groups()
#             date = datetime_module.date.fromisoformat(date_str)
#             return (date, name)
#         else:
#             return (None, folder_name)

#     async def get_dir(self, session: Session, root: pathlib.Path) -> pathlib.Path:

#         if self.parent_id is None:
#             return root / self.folder_name
#         else:
#             a = await (await self.read(session, self.parent_id)).get_dir(session, root)
#             return a / self.folder_name

#     async def get_parents(self, session: Session) -> list[typing.Self]:

#         if self.parent_id is None:
#             return []
#         else:
#             return (await self.parent.get_parents(session)) + [self.parent]

#     @classmethod
#     async def get_root_gallery(cls, session: Session, user_id: GalleryTypes.user_id) -> typing.Self | None:
#         return session.exec(select(cls).where(cls.user_id == user_id).where(cls.parent_id == None)).one_or_none()

#     @classmethod
#     async def api_get_is_available(cls, session: Session, gallery_available_admin: GalleryAdminGalleryAvailable) -> None:

#         # raise an exception if the parent gallery does not exist
#         if gallery_available_admin.parent_id:
#             if not await cls.read(session, gallery_available_admin.parent_id):
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND, detail='Parent gallery does not exist')

#         if session.exec(select(cls).where(cls._build_conditions(gallery_available_admin.model_dump()))).one_or_none():
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT, detail=cls.already_exists_message())

#     @classmethod
#     async def _check_authorization_new(cls, params):
#         if not params.admin:
#             if params.authorized_user_id != params.create_model.user_id:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to post gallery for another user')

#     async def _check_authorization_existing(self, params):

#         if not params.admin:
#             if params.authorized_user_id != self.user_id:

#                 if params.method == 'delete':
#                     raise HTTPException(
#                         status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

#                 gallery_permission = await GalleryPermission.read(params.session, (params.id, params.authorized_user_id))

#                 # if the gallery is private and user has no access, pretend it doesn't exist
#                 if not gallery_permission and self.visibility_level == config.VISIBILITY_LEVEL_NAME_MAPPING['private']:
#                     raise self.not_found_exception()

#                 elif params.method == 'get':
#                     if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['viewer']:
#                         raise HTTPException(
#                             status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

#                 elif params.method == 'patch':
#                     if gallery_permission.permission_level < config.PERMISSION_LEVEL_NAME_MAPPING['editor']:
#                         raise HTTPException(
#                             status.HTTP_401_UNAUTHORIZED, detail='Unauthorized to {method} this gallery'.format(method=params.method))

#     @classmethod
#     async def _check_validation_post(cls, params):
#         await cls.api_get_is_available(params.session, GalleryAdminGalleryAvailable(**params.create_model.model_dump(include=GalleryAdminGalleryAvailable.model_fields.keys(), exclude_unset=True)))

#     async def _check_validation_patch(self, params):
#         # take self, overwrite it with the update_model, and see if the combined model is available
#         await self.api_get_is_available(params.session, GalleryAdminGalleryAvailable(**{
#             **self.model_dump(include=list(GalleryAdminGalleryAvailable.model_fields.keys())), **params.update_model.model_dump(include=GalleryAdminGalleryAvailable.model_fields.keys(), exclude_unset=True)
#         }))

#     @classmethod
#     async def create(cls, params):
#         gallery = cls(
#             id=cls.generate_id(),
#             **params.create_model.model_dump()
#         )

#         if params.create_method_params == None:
#             params.create_method_params = GalleryAdminCreateParams()

#         if params.create_method_params.mkdir:
#             (await gallery.get_dir(params.session, params.c.galleries_dir)).mkdir()

#         return gallery

#     async def update(self, params) -> None:

#         rename_folder = False

#         # rename the folder
#         if 'name' in params.update_model.model_fields_set or 'date' in params.update_model.model_fields_set or 'parent_id' in params.update_model.model_fields_set:
#             rename_folder = True
#             original_dir = await self.get_dir(
#                 params.session, params.c.galleries_dir)

#         self.sqlmodelupdate(
#             params.update_model.model_dump(exclude_unset=True))

#         if rename_folder:
#             new_dir = (await self.get_dir(params.session, params.c.galleries_dir)).parent / self.folder_name
#             original_dir.rename(new_dir)

#     async def delete(self, params) -> None:

#         if params.delete_method_params == None:
#             params.delete_method_params = GalleryAdminCreateParams()

#         if params.delete_method_params.rmtree:
#             shutil.rmtree((await self.get_dir(params.session, params.c.galleries_dir)))

#     async def sync_with_local(self, session: Session, c: client.Client, dir: pathlib.Path) -> None:

#         if not dir.exists():
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail='Directory not found')

#         if self.folder_name != dir.name:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='Folder name does not match gallery name')

#         files: list[pathlib.Path] = []
#         dirs: list[pathlib.Path] = []
#         for item in dir.iterdir():
#             if item.is_dir():
#                 dirs.append(item)
#             if item.is_file():
#                 files.append(item)

#         # Add new galleries, remove old ones
#         local_galleries_by_folder_name = {
#             item.name: item for item in dirs}
#         db_galleries_by_folder_name = {
#             gallery.folder_name: gallery for gallery in self.children}

#         local_galleries_folder_names = set(
#             local_galleries_by_folder_name.keys())
#         db_galleries_folder_names = set(db_galleries_by_folder_name.keys())

#         toadd = local_galleries_folder_names - db_galleries_folder_names
#         to_remove = db_galleries_folder_names - local_galleries_folder_names

#         for folder_name in to_remove:
#             gallery = db_galleries_by_folder_name[folder_name]
#             await Gallery.api_delete(session=session, c=c, id=gallery._id, authorized_user_id=self.user_id, admin=False, delete_method_kwargs=GalleryAdminApiDeleteParams(rmtree=False))

#         for folder_name in toadd:
#             date, name = self.get_date_and_name_from_folder_name(
#                 folder_name)
#             new_gallery = await Gallery.api_post(
#                 session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=GalleryAdminCreate(name=name, user_id=self.user_id, visibility_level=self.visibility_level, parent_id=self.id, date=date),
#                 create_method_kwargs=GalleryAdminCreateParams(mkdir=False))

#         # add new files, remove old ones
#         local_file_by_names = {
#             file.name: file for file in files}
#         db_files_by_names = {
#             file.name: file for file in self.files}

#         local_file_names = set(local_file_by_names.keys())
#         db_file_names = set(db_files_by_names.keys())

#         toadd = local_file_names - db_file_names
#         to_remove = db_file_names - local_file_names

#         for file_name in to_remove:
#             file = db_files_by_names[file_name]

#             # if this is the last image tied to that version, delete the version too
#             if file.suffix in ImageFileMetadataConfig._SUFFIXES:
#                 image_version = await ImageVersion.read(session, file.image_file_metadata.version_id)
#                 if len(image_version.image_file_metadatas) == 1:
#                     await ImageVersion.api_delete(session=session, c=c, id=image_version.id, authorized_user_id=self.user_id, admin=False)

#             await File.api_delete(session=session, c=c, id=file.id, authorized_user_id=self.user_id, admin=False, unlink=False)

#         image_files: list[File] = []

#         for file_name in toadd:
#             stem = local_file_by_names[file_name].stem
#             suffix = ''.join(suffixes) if (
#                 suffixes := local_file_by_names[file_name].suffixes) else None

#             new_file = await File.api_post(
#                 session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=FileAdminCreate(stem=stem, suffix=suffix, gallery_id=self.id, size=local_file_by_names[file_name].stat().st_size))

#             # rename the file, just to make sure the suffix is lowercase
#             local_file_by_names[file_name].rename(
#                 local_file_by_names[file_name].with_name(new_file.name))

#             if suffix in ImageFileMetadataConfig._SUFFIXES:
#                 image_files.append(new_file)

#         # loop through files twice, adding the original images first
#         for original_images in [True, False]:
#             for image_file in image_files:

#                 base_name, version, scale = ImageFileMetadata.parse_file_stem(
#                     image_file.stem)

#                 if original_images == (version == None):

#                     parent_id = None
#                     if version is not None:
#                         image_version_og = session.exec(select(ImageVersion).where(ImageVersion.gallery_id == self._id).where(
#                             ImageVersion.base_name == base_name).where(ImageVersion.version == None)).one_or_none()

#                         # if an original exists, assume the version wants to link as the parent
#                         if image_version_og:
#                             parent_id = image_version_og._id

#                     image_version_kwargs = {
#                         'gallery_id': self.id,
#                         'base_name': base_name if parent_id is None else None,
#                         'version': version,
#                         'parent_id': parent_id
#                     }

#                     image_version = session.exec(select(ImageVersion).where(
#                         ImageVersion._build_conditions(image_version_kwargs))).one_or_none()

#                     # this if the first file of this version
#                     if not image_version:
#                         image_version = await ImageVersion.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageVersionAdminCreate(**image_version_kwargs))

#                     image_file_metadata = await ImageFileMetadata.api_post(session=session, c=c, authorized_user_id=self.user_id, admin=False, create_model=ImageFileMetadataAdminCreate(file_id=image_file.id, version_id=image_version.id, scale=scale))

#         # recursively sync children
#         for child in self.children:
#             await child.sync_with_local(session, c, dir / child.folder_name)
