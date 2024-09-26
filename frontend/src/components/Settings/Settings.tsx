import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/Auth';
import { Appearance } from './Appearance';
import { Sessions } from './Sessions';

import { IoBrush } from 'react-icons/io5';
import { IoRadioOutline } from 'react-icons/io5';

function Settings(): JSX.Element {
  const authContext = useContext(AuthContext);
  const defaultSelection = 'appearance';

  const [selection, setSelection] = useState<string>(defaultSelection);

  const baseSelectionComponentMapping = {
    appearance: {
      icon: <IoBrush />,
      name: 'Appearance',
      component: <Appearance />,
    },
  };

  const loggedInSelectionComponentMapping = {
    sessions: {
      icon: <IoRadioOutline />,
      name: 'Sessions',
      component: <Sessions />,
    },
  };

  useEffect(() => {
    if (
      authContext.state.user === null &&
      !(selection in loggedInSelectionComponentMapping)
    ) {
      setSelection(defaultSelection);
    }
  }, [authContext.state.user]);

  const selectionComponentMapping =
    authContext.state.user !== null
      ? {
          ...baseSelectionComponentMapping,
          ...loggedInSelectionComponentMapping,
        }
      : baseSelectionComponentMapping;

  if (!(selection in selectionComponentMapping)) {
    setSelection(defaultSelection);
  }

  return (
    <>
      <h1>Settings</h1>
      <div className="flex flex-row">
        <div className="flex flex-col">
          {Object.keys(selectionComponentMapping).map((key) => (
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
          ))}
          {/* Add more buttons for other settings options here */}
        </div>
        <div>{selectionComponentMapping[selection].component}</div>
      </div>
    </>
  );
}

export { Settings };
