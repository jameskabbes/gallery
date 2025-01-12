import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/request/magic-link/email/';
const API_METHOD = 'post';

type PostRequestMagicLinkEmailResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postRequestMagicLinkEmail(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostRequestMagicLinkEmailResponses[keyof PostRequestMagicLinkEmailResponses]
  >
> {
  return await callApi<
    PostRequestMagicLinkEmailResponses[keyof PostRequestMagicLinkEmailResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
}

export { postRequestMagicLinkEmail, PostRequestMagicLinkEmailResponses };
