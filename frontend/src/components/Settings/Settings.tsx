import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
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
  const navigate = useNavigate();

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

  const { selection: urlSelection } = useParams<{ selection: string }>();
  const [selection, setSelection] = useState<SelectionComponentKeys>(
    authContext.state.user
      ? defaultLoggedInSelection
      : defaultLoggedOutSelection
  );

  useEffect(() => {
    let validSelection = urlSelection as SelectionComponentKeys;
    if (!validSelection || !(validSelection in selectionComponentMapping)) {
      validSelection = authContext.state.user
        ? defaultLoggedInSelection
        : defaultLoggedOutSelection;
    }
    if (
      authContext.state.user === null &&
      loggedInComponentKeys.has(validSelection)
    ) {
      navigate('/settings/');
    } else {
      setSelection(validSelection);
    }
  }, [urlSelection, authContext.state.user, navigate]);

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

  return (
    <>
      <h1>Settings</h1>
      <div className="flex flex-row">
        <div className="flex flex-col">
          {Object.keys(selectionComponentMapping).map(
            (key: SelectionComponentKeys) => {
              if (authContext.state.user || !loggedInComponentKeys.has(key)) {
                return (
                  <Link to={`/settings/${key}`} key={key}>
                    <button
                      className={selection === key ? 'bg-color-darker' : ''}
                    >
                      <div className="flex flex-row space-x-1 items-center">
                        {selectionComponentMapping[key].icon}
                        <span>{selectionComponentMapping[key].name}</span>
                      </div>
                    </button>
                  </Link>
                );
              }
            }
          )}
        </div>
        <div>{selectionComponentMapping[selection].component}</div>
      </div>
    </>
  );
}

export { Settings };
