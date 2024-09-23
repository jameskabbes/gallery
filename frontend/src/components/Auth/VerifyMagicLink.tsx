import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { callApi, useApiCall } from '../../utils/Api';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';

const API_ENDPOINT = '/auth/verify-magic-link/';
const API_METHOD = 'post';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function VerifyMagicLink() {
  const access_token: string = new URLSearchParams(useLocation().search).get(
    'access_token'
  );

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_ENDPOINT.replace('{access_token}', access_token),
      method: API_METHOD,
      overwriteHeaders: {
        Authorization: `Bearer ${access_token}`,
      },
    },
    true,
    [access_token]
  );

  if (loading) {
    return (
      <div>
        <p>Verifying your magic link...</p>
      </div>
    );
  } else {
    if (response.status === 200) {
      return (
        <div>
          <p>Magic link verified!</p>
        </div>
      );
    } else {
      return (
        <div>
          <p>Magic link verification failed</p>
        </div>
      );
    }
  }
}

export { VerifyMagicLink };
