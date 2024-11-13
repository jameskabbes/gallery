import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';
import { callApi } from '../../utils/api';

const API_ENDPOINT = '/user/';
const API_METHOD = 'patch';

type PatchUserResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchUserFunc(
  authContext: AuthContextType,
  formData: Partial<
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >
): Promise<ApiResponse<PatchUserResponses[keyof PatchUserResponses]>> {
  return await callApi<
    PatchUserResponses[keyof PatchUserResponses],
    Partial<
      paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
    >
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    data: formData,
    authContext,
  });
}

export { patchUserFunc, PatchUserResponses };
