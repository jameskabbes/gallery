import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/';
const API_METHOD = 'get';

type GetAuthResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getAuth(
  authContext: AuthContextType
): Promise<ApiResponse<GetAuthResponses[keyof GetAuthResponses]>> {
  return await callApi<GetAuthResponses[keyof GetAuthResponses]>({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext: authContext,
  });
}

export { getAuth, GetAuthResponses };
