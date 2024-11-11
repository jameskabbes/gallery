import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/galleries/{gallery_id}/';
const API_METHOD = 'delete';

type DeleteGalleryResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteGallery(
  authContext: AuthContextType,
  gallery_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['gallery_id']
): Promise<ApiResponse<DeleteGalleryResponses[keyof DeleteGalleryResponses]>> {
  return await callApi<DeleteGalleryResponses[keyof DeleteGalleryResponses]>({
    endpoint: API_ENDPOINT.replace('{gallery_id}', gallery_id),
    method: API_METHOD,
    authContext,
  });
}

export { deleteGallery, DeleteGalleryResponses };
