import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { AuthContext, ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/users/available/username/{username}/';
const API_METHOD = 'get';

type AllResponseTypes = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function isUsernameAvailable(
  username: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['username']
): Promise<AllResponseTypes['200']['available']> {
  const { data, response } = await callApi<
    AllResponseTypes[keyof AllResponseTypes],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['username']
  >({
    endpoint: API_ENDPOINT.replace('{username}', username),
    method: API_METHOD,
    authContext: null,
  });

  if (response.status === 200) {
    const apiData = data as AllResponseTypes['200'];
    return apiData.available;
  }
}

export { isUsernameAvailable };
