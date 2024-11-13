import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/logout/';
const API_METHOD = 'post';

type PostLogOutResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogOut(
  authContext: AuthContextType
): Promise<ApiResponse<PostLogOutResponses[keyof PostLogOutResponses]>> {
  return await callApi<PostLogOutResponses[keyof PostLogOutResponses]>({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
  });
}

export { postLogOut, PostLogOutResponses };
