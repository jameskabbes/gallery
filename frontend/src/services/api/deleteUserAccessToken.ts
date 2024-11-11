import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContext,
  ExtractResponseTypes,
  ToastContext,
} from '../../types';

const API_ENDPOINT = '/user-access-tokens/{user_access_token_id}/';
const API_METHOD = 'delete';

type DeleteUserAccessTokenResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteUserAccessToken(
  authContext: AuthContext,
  userAccessTokenId: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['user_access_token_id']
): Promise<
  ApiResponse<
    DeleteUserAccessTokenResponses[keyof DeleteUserAccessTokenResponses]
  >
> {
  return await callApi<
    DeleteUserAccessTokenResponses[keyof DeleteUserAccessTokenResponses]
  >({
    endpoint: API_ENDPOINT.replace('{user_access_token_id}', userAccessTokenId),
    method: API_METHOD,
    authContext,
  });
}

export { deleteUserAccessToken, DeleteUserAccessTokenResponses };
