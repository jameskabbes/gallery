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
    url: API_ENDPOINT.replace('{username}', username),
    method: API_METHOD,
    authContext: null,
  });
}

async function isUsernameAvailable(
  username: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['username']
): Promise<boolean> {
  const response = await getIsUsernameAvailable(username);
  if (response.status == 200) {
    return true;
  } else {
    return false;
  }
}

export { getIsUsernameAvailable };
