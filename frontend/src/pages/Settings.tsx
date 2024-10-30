import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../contexts/Auth';
import { ToastContext } from '../contexts/Toast';
import { Appearance } from '../components/Settings/Appearance';
import { UserAccessTokens } from '../components/Settings/UserAccessTokens';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/Api';
import { Profile } from '../components/Settings/Profile';
import { DeviceContext } from '../contexts/Device';

import { IoBrush } from 'react-icons/io5';
import { IoRadioOutline } from 'react-icons/io5';
import { IoPersonOutline } from 'react-icons/io5';
import { IoKeyOutline } from 'react-icons/io5';
import { APIKeys } from '../components/Settings/APIKeys';
import { Card1 } from '../components/Utils/Card';
import { Surface } from '../components/Utils/Surface';

const API_ENDPOINT = '/settings/page/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Settings(): JSX.Element {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const navigate = useNavigate();

  const {
    data: apiData,
    loading,
    response,
  } = useApiCall<ResponseTypesByStatus[keyof ResponseTypesByStatus]>({
    endpoint: API_ENDPOINT,
    method: API_METHOD,
  });

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
    sessions: {
      icon: <IoRadioOutline />,
      name: 'Sessions',
      component: (
        <UserAccessTokens
          authContext={authContext}
          toastContext={toastContext}
        />
      ),
    },
    'api-keys': {
      icon: <IoKeyOutline />,
      name: 'API Keys',
      component: (
        <APIKeys authContext={authContext} toastContext={toastContext} />
      ),
    },
  };

  type SelectionComponentKeys = keyof typeof selectionComponentMapping;
  const loggedInComponentKeys = new Set<SelectionComponentKeys>([
    'profile',
    'sessions',
    'api-keys',
  ]);

  const defaultLoggedInSelection: SelectionComponentKeys = 'profile';
  const defaultLoggedOutSelection: SelectionComponentKeys = 'appearance';

  const [selection, setSelection] = useState<SelectionComponentKeys>(
    useParams<{ selection: string }>().selection as SelectionComponentKeys
  );

  useEffect(() => {
    if (!loading && selection in selectionComponentMapping) {
      navigate(`/settings/${selection}`);
    }
  }, [selection, loading]);

  useEffect(() => {
    if (!loading) {
      // logged out
      if (authContext.state.user === null) {
        if (
          loggedInComponentKeys.has(selection) ||
          !(selection in selectionComponentMapping)
        ) {
          setSelection(defaultLoggedOutSelection);
        }
      } else {
        if (!(selection in selectionComponentMapping)) {
          setSelection(defaultLoggedInSelection);
        }
      }
    }
  }, [authContext.state.user, selection, loading]);

  return (
    <div className="max-w-screen-2xl">
      {loading || !selection ? (
        'loading'
      ) : (
        <div>
          <div className="flex flex-row space-x-4 overflow-x-auto">
            {Object.keys(selectionComponentMapping).map(
              (key: SelectionComponentKeys) => {
                if (authContext.state.user || !loggedInComponentKeys.has(key)) {
                  {
                    selectionComponentMapping[key].component;
                  }

                  return (
                    <button
                      key={key}
                      onClick={() => setSelection(key)}
                      className={`${
                        selection === key ? 'border-color-primary' : ''
                      } border-b-[1px] m-2 hover:border-color-primary`}
                    >
                      <h5>
                        <div className="flex flex-row space-x-1 items-center">
                          {selectionComponentMapping[key].icon}
                          <span className="whitespace-nowrap">
                            {selectionComponentMapping[key].name}
                          </span>
                        </div>
                      </h5>
                    </button>
                  );
                }
              }
            )}
          </div>
          <Surface>
            <hr />
          </Surface>
          <div className="p-2">
            {selectionComponentMapping[selection].component}
          </div>
        </div>
      )}
    </div>
  );
}

export { Settings };
