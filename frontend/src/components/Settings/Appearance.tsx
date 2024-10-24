import React, { useContext, useEffect, useState } from 'react';
import { DarkModeContext } from '../../contexts/DarkMode';

import { IoSunnyOutline } from 'react-icons/io5';
import { IoMoonOutline } from 'react-icons/io5';
import { IoSettingsOutline } from 'react-icons/io5';
import {
  DarkModeContext as DarkModeContextType,
  defaultInputState,
  InputState,
} from '../../types';
// import { InputRadio } from '../Form/InputRadio';

interface ThemeOption {
  value: DarkModeContextType['preference'];
  icon: JSX.Element;
  label: JSX.Element;
}

function DarkModeToggle() {
  // initialize dark mode with the client's system/app preferences

  const darkModeContext = useContext(DarkModeContext);
  const themeOptions: ThemeOption[] = [
    {
      value: 'light',
      icon: <IoSunnyOutline />,
      label: <span>Light</span>,
    },
    {
      value: 'system',
      icon: <IoSettingsOutline />,
      label: (
        <span>{`System (${
          darkModeContext.systemState ? 'dark' : 'light'
        })`}</span>
      ),
    },
    { value: 'dark', icon: <IoMoonOutline />, label: <span>Dark</span> },
  ];

  type ThemeOptionValue = ThemeOption['value'];
  const [theme, setTheme] = useState<InputState<ThemeOptionValue>>({
    ...defaultInputState<ThemeOptionValue>(darkModeContext.preference),
  });

  useEffect(() => {
    darkModeContext.setPreference(theme.value);
  }, [theme.value]);

  return (
    <>
      <h2>Theme</h2>
      {/* make a radio selector */}

      <form className="flex flex-col">
        <fieldset name="theme">
          {themeOptions.map((option) => (
            <label key={option.value}>
              {/* <InputRadio
                value={option.value}
                checked={theme.value === option.value}
                setState={setTheme}
              >
                <div className="flex flex-row items-center space-x-2">
                  {option.icon}
                  {option.label}
                </div>
              </InputRadio> */}
            </label>
          ))}
        </fieldset>
      </form>
    </>
  );
}

function Appearance() {
  const darkModeContext = useContext(DarkModeContext);

  return <DarkModeToggle />;
}

export { Appearance };
