import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../contexts/Auth';
import { ToastContext } from '../../contexts/Toast';
import { Appearance } from './Appearance';
import { UserAccessTokens } from './UserAccessTokens';
import { paths, operations, components } from '../../openapi_schema';
import { ExtractResponseTypes } from '../../types';
import { useApiCall } from '../../utils/Api';
import { Profile } from './Profile';

import { IoBrush } from 'react-icons/io5';
import { IoRadioOutline } from 'react-icons/io5';
import { IoPersonOutline } from 'react-icons/io5';
import { IoKeyOutline } from 'react-icons/io5';
import { APIKeys } from './APIKeys';

const API_ENDPOINT = '/settings/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Settings(): JSX.Element {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const selectionComponentMapping = {
    profile: {
      icon: <IoPersonOutline />,
      name: 'Profile',
      component: (
        <Profile authContext={authContext} toastContext={toastContext} />
      ),
    },
    appearance: {
      icon: <IoBrush />,
      name: 'Appearance',
      component: <Appearance />,
    },
    UserAccessTokens: {
      icon: <IoRadioOutline />,
      name: 'UserAccessTokens',
      component: (
        <UserAccessTokens
          authContext={authContext}
          toastContext={toastContext}
        />
      ),
    },
    apiKeys: {
      icon: <IoKeyOutline />,
      name: 'API Keys',
      component: (
        <APIKeys authContext={authContext} toastContext={toastContext} />
      ),
    },
  };

  const loggedInComponentKeys = new Set([
    'profile',
    'UserAccessTokens',
    'apiKeys',
  ]);

  const defaultSelection = 'appearance';
  const [selection, setSelection] = useState(defaultSelection);

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>(
    {
      endpoint: API_ENDPOINT,
      method: API_METHOD,
    },
    true
  );

  useEffect(() => {
    if (
      authContext.state.user === null &&
      loggedInComponentKeys.has(selection)
    ) {
      setSelection(defaultSelection);
    }
  }, [authContext.state.user]);

  return (
    <>
      <h1>Settings</h1>
      <div className="flex flex-row">
        <div className="flex flex-col">
          {Object.keys(selectionComponentMapping).map((key) => {
            if (authContext.state.user || !loggedInComponentKeys.has(key)) {
              return (
                <button
                  key={key}
                  onClick={() => setSelection(key)}
                  className={selection === key ? 'bg-color-darker' : ''}
                >
                  <div className="flex flex-row space-x-1 items-center">
                    {selectionComponentMapping[key].icon}
                    <span>{selectionComponentMapping[key].name}</span>
                  </div>
                </button>
              );
            }
          })}
        </div>
        <div>{selectionComponentMapping[selection].component}</div>
      </div>
    </>
  );
}

export { Settings };
