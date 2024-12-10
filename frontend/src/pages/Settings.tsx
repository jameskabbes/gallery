import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/Auth';
import { ToastContext } from '../contexts/Toast';
import { Appearance } from '../components/Settings/Appearance';
import { UserAccessTokens } from '../components/Settings/UserAccessTokens';
import { paths, operations, components } from '../openapi_schema';
import { ExtractResponseTypes } from '../types';
import { useApiCall } from '../utils/api';
import { Profile } from '../components/Settings/Profile';
import { DeviceContext } from '../contexts/Device';

import { IoBrush } from 'react-icons/io5';
import { IoRadioOutline } from 'react-icons/io5';
import { IoPersonOutline } from 'react-icons/io5';
import { IoKeyOutline } from 'react-icons/io5';
import { ApiKeys } from '../components/Settings/ApiKeys';
import { Card1 } from '../components/Utils/Card';
import { Surface } from '../components/Utils/Surface';

const API_ENDPOINT = '/pages/settings/';
const API_METHOD = 'get';

type ResponseTypesByStatus = ExtractResponseTypes<
  paths[typeof API_ENDPOINT][typeof API_METHOD]['responses']
>;

function Settings(): JSX.Element {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const navigate = useNavigate();

  const { data, loading, status } = useApiCall<
    ResponseTypesByStatus[keyof ResponseTypesByStatus]
  >({
    url: API_ENDPOINT,
    method: API_METHOD,
  });

  const selectionComponentMapping = {
    profile: {
      icon: <IoPersonOutline />,
      name: 'Profile',
      requiresAuth: true,
      component: (
        <Profile authContext={authContext} toastContext={toastContext} />
      ),
    },
    appearance: {
      icon: <IoBrush />,
      name: 'Appearance',
      requiresAuth: false,
      component: <Appearance />,
    },
    sessions: {
      icon: <IoRadioOutline />,
      name: 'Sessions',
      requiresAuth: true,
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
      requiresAuth: true,
      component: (
        <ApiKeys authContext={authContext} toastContext={toastContext} />
      ),
    },
  };

  type SelectionComponentKey = keyof typeof selectionComponentMapping;

  function navigateToSelection(selection: SelectionComponentKey) {
    navigate(`/settings/${selection}`);
  }

  const selection = useParams<{ selection: string }>()
    .selection as SelectionComponentKey;
  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (!loading) {
      if (authContext.state.user === null) {
        if (
          !(selection in selectionComponentMapping) ||
          selectionComponentMapping[selection].requiresAuth
        ) {
          navigateToSelection('appearance');
        } else {
          setValidated(true);
        }
      } else {
        if (!(selection in selectionComponentMapping)) {
          navigateToSelection('profile');
        } else {
          setValidated(true);
        }
      }
    }
  }, [authContext.state.user, loading, selection]);

  return (
    <div className="max-w-screen-2xl mx-auto w-full">
      {loading || !validated ? (
        'loading'
      ) : (
        <div>
          <div className="flex flex-row overflow-x-auto ">
            {Object.keys(selectionComponentMapping).map(
              (key: SelectionComponentKey) => {
                if (
                  authContext.state.user ||
                  !selectionComponentMapping[key].requiresAuth
                ) {
                  {
                    selectionComponentMapping[key].component;
                  }

                  return (
                    <Surface key={key}>
                      <button
                        onClick={() => navigateToSelection(key)}
                        className={`${
                          selection === key ? 'border-color-primary' : ''
                        } border-[1px] hover:border-color-primary py-1 px-2 mx-1 my-2 rounded-full `}
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
                    </Surface>
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
