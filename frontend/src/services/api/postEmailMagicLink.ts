import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/email-magic-link/';
const API_METHOD = 'post';

type PostEmailMagicLinkResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postEmailMagicLink(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<PostEmailMagicLinkResponses[keyof PostEmailMagicLinkResponses]>
> {
  return await callApi<
    PostEmailMagicLinkResponses[keyof PostEmailMagicLinkResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postEmailMagicLink, PostEmailMagicLinkResponses };
