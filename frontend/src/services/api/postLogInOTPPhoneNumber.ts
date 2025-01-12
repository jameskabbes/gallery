import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import {
  ApiResponse,
  AuthContextType,
  ExtractResponseTypes,
} from '../../types';

const API_ENDPOINT = '/auth/login/otp/phone_number/';
const API_METHOD = 'post';

type PostLoginOTPPhoneNumberResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function postLogInOTPPhoneNumber(
  authContext: AuthContextType,
  data: paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
): Promise<
  ApiResponse<
    PostLoginOTPPhoneNumberResponses[keyof PostLoginOTPPhoneNumberResponses]
  >
> {
  const response = await callApi<
    PostLoginOTPPhoneNumberResponses[keyof PostLoginOTPPhoneNumberResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
    authContext,
    data,
  });
  authContext.updateFromApiResponse(response.data);
  return response;
}

export { postLogInOTPPhoneNumber, PostLoginOTPPhoneNumberResponses };
