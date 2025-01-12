import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request/signup/sms/';
const API_METHOD = 'post';

type PostRequestSignUpSMSResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestSignUpSMS(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostRequestSignUpSMSResponses[keyof PostRequestSignUpSMSResponses]
  >
> {
  return await callApi<
    PostRequestSignUpSMSResponses[keyof PostRequestSignUpSMSResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestSignUpSMS, PostRequestSignUpSMSResponses };
