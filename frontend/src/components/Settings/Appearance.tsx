import React, { useContext, useEffect, useState } from 'react';
import { DarkModeContext } from '../../contexts/DarkMode';
import { IoSunnyOutline } from 'react-icons/io5';
import { IoMoonOutline } from 'react-icons/io5';
import { IoSettingsOutline } from 'react-icons/io5';
import { DarkModeContextType } from '../../types';
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

  return (
    <>
      <h2 className="mb-4">Appearance</h2>
      <h3>Theme</h3>
      <div className="flex flex-row">
        <form>
          <fieldset name="theme" className="space-y-1">
            {themeOptions.map((option) => (
              <label
                key={option.value}
                className="flex flex-row space-x-2 items-center cursor-pointer"
              >
                <RadioButton1
                  state={darkModeContext.preference === option.value}
                >
                  <input
                    type="radio"
                    value={option.value}
                    checked={darkModeContext.preference === option.value}
                    onChange={() => darkModeContext.setPreference(option.value)}
                    className="opacity-0 absolute h-0 w-0"
                  />
                </RadioButton1>
                {option.icon}
                {option.label}
              </label>
            ))}
          </fieldset>
        </form>
      </div>
    </>
  );
}

export function Appearance() {
  const darkModeContext = useContext(DarkModeContext);
  return <DarkModeToggle />;
}
