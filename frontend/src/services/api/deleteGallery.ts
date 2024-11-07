import React, { useState, useContext, useEffect } from 'react';
import { callApi } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { CallApiReturn, ExtractResponseTypes, ToastContext } from '../../types';
import { AuthContext } from '../../types';

const API_ENDPOINT = '/galleries/{gallery_id}/';
const API_METHOD = 'delete';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

async function deleteGallery(
  authContext: AuthContext,
  gallery_id: paths[typeof API_ENDPOINT][typeof API_METHOD]['parameters']['path']['gallery_id']
): Promise<CallApiReturn<ResponseTypesByStatus[keyof ResponseTypesByStatus]>> {
  const { data, response } = await callApi<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    endpoint: API_ENDPOINT.replace('{gallery_id}', gallery_id),
    method: API_METHOD,
    authContext,
  });

  return { data, response };
}

export { deleteGallery, ResponseTypesByStatus };
