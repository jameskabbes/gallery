import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/users/me/';
const API_METHOD = 'delete';

type DeleteUserResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteUser(
  authContext: AuthContextType
): Promise<ApiResponse<DeleteUserResponses[keyof DeleteUserResponses]>> {
  return await callApi<DeleteUserResponses[keyof DeleteUserResponses]>({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
  });
}

export { deleteUser, DeleteUserResponses };
