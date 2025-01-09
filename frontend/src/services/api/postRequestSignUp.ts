import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request-signup/';
const API_METHOD = 'post';

type PostRequestSignUpResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestSignUp(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<PostRequestSignUpResponses[keyof PostRequestSignUpResponses]>
> {
  return await callApi<
    PostRequestSignUpResponses[keyof PostRequestSignUpResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestSignUp, PostRequestSignUpResponses };
