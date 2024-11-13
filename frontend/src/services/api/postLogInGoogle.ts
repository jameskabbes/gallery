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

type PostLoginGoogleResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogInGoogle(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<PostLoginGoogleResponses[keyof PostLoginGoogleResponses]>
> {
  return await callApi<
    PostLoginGoogleResponses[keyof PostLoginGoogleResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postLogInGoogle, PostLoginGoogleResponses };
