import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/password/';
const API_METHOD = 'post';

type PostLogInResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogin(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
): Promise<ApiResponse<PostLogInResponses[keyof PostLogInResponses]>> {
  const formData = new URLSearchParams();
  Object.keys(data).forEach((key) => {
    formData.append(key, data[key].toString());
  });

  return await callApi<
    PostLogInResponses[keyof PostLogInResponses],
    URLSearchParams
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data: formData,
  });
}

export { postLogin, PostLogInResponses };
