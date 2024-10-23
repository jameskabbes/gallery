import React from 'react';
import { Surface } from '../Utils/Surface';
import { BaseInputProps } from './Input';

interface InputRadioProps<T extends string> {
  setState: BaseInputProps<T>['setState'];
  value: T;
  checked: boolean;
  children: React.ReactNode;
}

function InputRadio<T extends string>({
  setState,
  value,
  checked,
  children,
}: InputRadioProps<T>) {
  return (
    <div className="flex flex-row items-center space-x-2">
      <Surface keepParentMode={true}>
        <div
          className="input-radio-container rounded-full"
          style={{
            borderWidth: '0.0625em',
            width: '1em',
            height: '1em',
            margin: '0',
            padding: '0.1em',
          }}
        >
          <input
            type="radio"
            value={value}
            checked={checked}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              if (e.target.checked) {
                setState((prev) => ({ ...prev, value: value }));
              }
            }}
            className="opacity-0 absolute"
          />

          <div
            className={`h-full w-full rounded-full ${
              checked && 'bg-primary-light dark:bg-primary-light'
            } `}
            style={{
              transition: '0.1s',
            }}
          ></div>
        </div>
      </Surface>
      {children}
    </div>
  );
}

export { InputRadio };
