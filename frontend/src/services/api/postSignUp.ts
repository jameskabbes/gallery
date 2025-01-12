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

type PostSignUpData =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json'];

async function postSignUp(
  authContext: AuthContextType,
  data: PostSignUpData
): Promise<ApiResponse<PostSignUpResponses[keyof PostSignUpResponses]>> {
  return await callApi<PostSignUpResponses[keyof PostSignUpResponses]>({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data: data,
  });
}

export { postSignUp, PostSignUpResponses, PostSignUpData };
