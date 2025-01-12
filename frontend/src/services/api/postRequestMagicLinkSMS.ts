import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request/magic-link/sms/';
const API_METHOD = 'post';

type PostRequestMagicLinkSMSResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestMagicLinkSMS(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostRequestMagicLinkSMSResponses[keyof PostRequestMagicLinkSMSResponses]
  >
> {
  return await callApi<
    PostRequestMagicLinkSMSResponses[keyof PostRequestMagicLinkSMSResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestMagicLinkSMS, PostRequestMagicLinkSMSResponses };
