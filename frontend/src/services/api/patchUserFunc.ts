import React, { Component } from 'react';
import { paths, operations, components } from '../../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../../types';
import { callApi } from '../../utils/api';
import { AuthContext } from '../../types';

const API_ENDPOINT = '/user/';
const API_METHOD = 'patch';

type PatchUserResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function patchUserFunc(
  authContext: AuthContext,
  formData: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<ApiResponse<PatchUserResponses[keyof PatchUserResponses]>> {
  return await callApi<
    PatchUserResponses[keyof PatchUserResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
    data: formData,
    authContext,
  });
}

export { patchUserFunc, PatchUserResponses };
