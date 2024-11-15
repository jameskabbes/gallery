import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/galleries/available/';
const API_METHOD = 'get';

type GetIsGalleryAvailableResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getIsGalleryAvailable(
  authContext: AuthContextType,
  galleryAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    GetIsGalleryAvailableResponses[keyof GetIsGalleryAvailableResponses]
  >
> {
  return await callApi<
    GetIsGalleryAvailableResponses[keyof GetIsGalleryAvailableResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    data: galleryAvailable,
    authContext: authContext,
  });
}

async function isGalleryAvailable(
  authContext: AuthContextType,
  galleryAvailable: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<boolean> {
  const response = await getIsGalleryAvailable(authContext, galleryAvailable);
  if (response.status == 200) {
    const data = response.data as GetIsGalleryAvailableResponses['200'];
    return data.available;
  } else {
    return false;
  }
}

export { getIsGalleryAvailable, isGalleryAvailable };
