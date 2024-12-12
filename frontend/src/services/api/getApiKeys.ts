import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/api-keys/';
const API_METHOD = 'get';

type GetApiKeysResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

type QueryParams =
  paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['query'];

async function getApiKeys(
  authContext: AuthContextType,
  params: Partial<QueryParams>
): Promise<ApiResponse<GetApiKeysResponses[keyof GetApiKeysResponses]>> {
  return await callApi<GetApiKeysResponses[keyof GetApiKeysResponses]>({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext: authContext,
    params: params,
  });
}

export { getApiKeys, QueryParams, GetApiKeysResponses };
