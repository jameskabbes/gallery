import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/signup/';
const API_METHOD = 'post';

type PostSignUpResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postSignUp(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/x-www-form-urlencoded']
): Promise<ApiResponse<PostSignUpResponses[keyof PostSignUpResponses]>> {
  const formData = new URLSearchParams();
  Object.keys(data).forEach((key) => {
    formData.append(key, data[key].toString());
  });

  return await callApi<
    PostSignUpResponses[keyof PostSignUpResponses],
    URLSearchParams
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data: formData,
  });
}

export { postSignUp, PostSignUpResponses };
