import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/galleries/';
const API_METHOD = 'post';

type PostGalleryResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postGallery(
  authContext: AuthContextType,
  galleryCreate: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<ApiResponse<PostGalleryResponses[keyof PostGalleryResponses]>> {
  return await callApi<
    PostGalleryResponses[keyof PostGalleryResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data: galleryCreate,
  });
}

export { postGallery, PostGalleryResponses };
