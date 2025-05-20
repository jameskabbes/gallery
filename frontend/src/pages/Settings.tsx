import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/Auth';
import { ToastContext } from '../contexts/Toast';
import { Appearance } from '../components/Settings/Appearance';
import { UserAccessTokens } from '../components/Settings/UserAccessTokens';
import { Profile } from '../components/Settings/Profile';
import { paths, operations, components } from '../openapi_schema';

import { IoBrush } from 'react-icons/io5';
import { IoRadioOutline } from 'react-icons/io5';
import { IoPersonOutline } from 'react-icons/io5';
import { IoKeyOutline } from 'react-icons/io5';
import { ApiKeys } from '../components/Settings/ApiKeys';
import { useApiCall } from '../utils/api';
import { Surface } from '../components/Utils/Surface';
import { Button2 } from '../components/Utils/Button';
import { getSettingsPage } from '../services/apiServices';

export function Settings(): JSX.Element {
  const authContext = useContext(AuthContext);
  const toastContext = useContext(ToastContext);
  const navigate = useNavigate();

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
  const { loading } = useApiCall(getSettingsPage, { authContext });

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
    <>
      {validated && (
        <div className="flex-1 max-w-screen-2xl mx-auto w-full px-1">
          <div className="flex flex-row overflow-x-auto space-x-1 py-2">
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
                    <Button2
                      key={key}
                      className="rounded-full"
                      onClick={() => navigateToSelection(key)}
                      isActive={selection === key}
                    >
                      <div className="flex flex-row space-x-1 items-center">
                        {selectionComponentMapping[key].icon}
                        <span className="whitespace-nowrap">
                          {selectionComponentMapping[key].name}
                        </span>
                      </div>
                    </Button2>
                  );
                }
              }
            )}
          </div>
          <Surface>
            <hr />
          </Surface>
          {selection && (
            <div className="p-2">
              {selectionComponentMapping[selection].component}
            </div>
          )}
        </div>
      )}
    </>
  );
}
