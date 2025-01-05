import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/google/';
const API_METHOD = 'post';

type PostLoginMagicLinkResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogInWithMagicLink(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<PostLoginMagicLinkResponses[keyof PostLoginMagicLinkResponses]>
> {
  return await callApi<
    PostLoginMagicLinkResponses[keyof PostLoginMagicLinkResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    headers: {
      Authorization: `Bearer ${data.access_token}`,
    },
  });
}

export { postLogInWithMagicLink, PostLoginMagicLinkResponses };
