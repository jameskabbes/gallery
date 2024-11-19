import React, { useContext, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { callApi, useApiCall } from '../../utils/api';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { GlobalModalsContext } from '../../contexts/GlobalModals';
import { Loader1 } from '../Utils/Loader';
import { IoWarning } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';

const API_ENDPOINT = '/auth/verify-magic-link/';
const API_METHOD = 'post';

type PostVerifyMagicLinkResponses = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function VerifyMagicLink() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const access_token: string = searchParams.get('access_token');
  const stay_signed_in = searchParams.get('stay_signed_in') === 'True';
  const globalModalsContext = useContext(GlobalModalsContext);

  const { data, loading, status } = useApiCall<
    PostVerifyMagicLinkResponses[keyof PostVerifyMagicLinkResponses],
    paths[typeof API_ENDPOINT][typeof API_METHOD]['requestBody']['content']['application/json']
  >(
    {
      url: API_ENDPOINT,
      method: API_METHOD,
      data: {
        stay_signed_in: stay_signed_in,
      },
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    },
    [access_token, stay_signed_in]
  );

  function Component() {
    let Icon;
    let message;

    if (loading) {
      Icon = () => <Loader1 />;
      message = 'Verifying your magic link';
    } else {
      if (status === 200) {
        Icon = () => <IoCheckmark className="text-green-500" />;
        message = 'Magic link verified. You can close this tab';
      } else {
        Icon = () => <IoWarning className="text-red-500" />;
        message = 'Could not verify magic link';
        if (status === 401) {
          const apiData = data as PostVerifyMagicLinkResponses[401];
          message = apiData.detail;
        }
      }
    }

    return (
      <div className="flex flex-col items-center space-y-2">
        <h1>
          <Icon />
        </h1>
        <h4 className="text-center">{message}</h4>
      </div>
    );
  }

  useEffect(() => {
    globalModalsContext.setModal({
      component: <Component />,
      contentStyle: { maxWidth: '400px', width: '100%' },
      includeExitButton: true,
      key: 'verify-magic-link-loading',
    });
  }, [loading]);

  return null;
}

export { VerifyMagicLink };
