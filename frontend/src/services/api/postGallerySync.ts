import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/galleries/{gallery_id}/sync/';
const API_METHOD = 'post';

type PostGallerySyncResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postGallerySync(
  authContext: AuthContextType,
  galleryId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['gallery_id']
): Promise<
  ApiResponse<PostGallerySyncResponses[keyof PostGallerySyncResponses]>
> {
  return await callApi<
    PostGallerySyncResponses[keyof PostGallerySyncResponses]
  >({
    url: API_ENDPOINT.replace('{gallery_id}', galleryId),
    method: API_METHOD,
    authContext,
  });
}

export { postGallerySync, PostGallerySyncResponses };
