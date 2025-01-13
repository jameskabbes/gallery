import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/magic-link/';
const API_METHOD = 'post';

type PostLoginMagicLinkResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogInMagicLink(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
): Promise<
  ApiResponse<PostLoginMagicLinkResponses[keyof PostLoginMagicLinkResponses]>
> {
  const response = await callApi<
    PostLoginMagicLinkResponses[keyof PostLoginMagicLinkResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });

  authContext.updateFromApiResponse(response.data);
  return response;
}

export { postLogInMagicLink, PostLoginMagicLinkResponses };
