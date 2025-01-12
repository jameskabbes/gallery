import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/otp/email/';
const API_METHOD = 'post';

type PostLoginOTPEmailResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogInOTPEmail(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<PostLoginOTPEmailResponses[keyof PostLoginOTPEmailResponses]>
> {
  const response = await callApi<
    PostLoginOTPEmailResponses[keyof PostLoginOTPEmailResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });

  authContext.updateFromApiResponse(response.data);
  return response;
}

export { postLogInOTPEmail, PostLoginOTPEmailResponses };
