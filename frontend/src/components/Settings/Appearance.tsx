import React, { useContext, useEffect, useState } from 'react';
import { DarkModeContext } from '../../contexts/DarkMode';
import { IoSunnyOutline } from 'react-icons/io5';
import { IoMoonOutline } from 'react-icons/io5';
import { IoSettingsOutline } from 'react-icons/io5';
import { DarkModeContext as DarkModeContextType } from '../../types';
import { RadioButton1 } from '../Utils/RadioButton';

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

  const [theme, setTheme] = useState<DarkModeContextType['preference']>(
    darkModeContext.preference
  );

  useEffect(() => {
    darkModeContext.setPreference(theme);
  }, [theme]);

  return (
    <>
      <h2>Theme</h2>

      <form className="flex flex-col">
        <fieldset name="theme">
          {themeOptions.map((option) => (
            <div
              className="flex flex-row space-x-4 items-center"
              onClick={() => setTheme(option.value)}
              key={'theme-' + option.value}
            >
              <RadioButton1 state={theme === option.value}>
                <input
                  type="radio"
                  value={option.value}
                  checked={theme === option.value}
                  onChange={() => setTheme(option.value)}
                  className="opacity-0 absolute h-0 w-0"
                />
              </RadioButton1>
              <label key={option.value} className="relative">
                <div className="flex flex-row items-center space-x-2">
                  {option.icon}
                  {option.label}
                </div>
              </label>
            </div>
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
