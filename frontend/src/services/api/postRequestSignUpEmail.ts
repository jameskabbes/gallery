import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request/signup/email/';
const API_METHOD = 'post';

type PostRequestSignUpEmailResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestSignUpEmail(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostRequestSignUpEmailResponses[keyof PostRequestSignUpEmailResponses]
  >
> {
  return await callApi<
    PostRequestSignUpEmailResponses[keyof PostRequestSignUpEmailResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestSignUpEmail, PostRequestSignUpEmailResponses };
