import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import { ApiResponse, ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/users/available/email/{email}/';
const API_METHOD = 'get';

type GetIsEmailAvailableResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function getIsEmailAvailable(
  email: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['email']
): Promise<
  ApiResponse<GetIsEmailAvailableResponses[keyof GetIsEmailAvailableResponses]>
> {
  return await callApi<
    GetIsEmailAvailableResponses[keyof GetIsEmailAvailableResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['email']
  >({
    url: API_ENDPOINT.replace('{email}', email),
    method: API_METHOD,
  });
}

async function isEmailAvailable(
  email: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['email']
): Promise<boolean> {
  const response = await getIsEmailAvailable(email);
  if (response.status == 200) {
    return true;
  } else {
    return false;
  }
}

export { getIsEmailAvailable, isEmailAvailable };
