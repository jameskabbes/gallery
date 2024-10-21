import React, { useState, useEffect } from 'react';

import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, InputProps } from './Input';
import { Surface } from '../Utils/Surface';

type T = boolean;

interface InputCheckboxProps extends BaseInputProps<T> {
  showValidity?: boolean;
}

function InputCheckbox({
  state,
  setState,
  showValidity = false,
  ...rest
}: InputCheckboxProps) {
  return (
    <div className="flex flex-row items-center space-x-2">
      <Surface>
        <div
          className="input-checkbox-container hover:border-color-primary"
          onClick={() => setState((prev) => ({ ...prev, value: !prev.value }))}
          style={{
            borderRadius: '0.25em',
            borderWidth: '0.0625em',
            width: '1em',
            height: '1em',
            margin: '0',
            padding: '0.1em',
          }}
        >
          <Input
            state={state}
            setState={setState}
            checked={state.value}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              let newValue: InputCheckboxProps['state']['value'] =
                e.target.checked;
              setState({
                ...state,
                value: newValue,
              });
            }}
            className="opacity-0 absolute"
            {...rest}
          />
          <div
            className={`h-full w-full ${state.value && 'bg-color-primary'} `}
            style={{
              transition: '0.1s',
              borderRadius: '0.125em',
            }}
          ></div>
        </div>
      </Surface>
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputCheckbox, InputCheckboxProps };
