import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request-magic-link/';
const API_METHOD = 'post';

type PostRequestMagicLinkResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestMagicLink(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostRequestMagicLinkResponses[keyof PostRequestMagicLinkResponses]
  >
> {
  return await callApi<
    PostRequestMagicLinkResponses[keyof PostRequestMagicLinkResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestMagicLink, PostRequestMagicLinkResponses };
