import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/users/available/username/{username}/';
const API_METHOD = 'get';

type GetIsUsernameAvailable = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getIsUsernameAvailable(
  username: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['username']
): Promise<ApiResponse<GetIsUsernameAvailable[keyof GetIsUsernameAvailable]>> {
  return await callApi<
    GetIsUsernameAvailable[keyof GetIsUsernameAvailable],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['username']
  >({
    endpoint: API_ENDPOINT.replace('{username}', username),
    method: API_METHOD,
    authContext: null,
  });
}

export { getIsUsernameAvailable };
