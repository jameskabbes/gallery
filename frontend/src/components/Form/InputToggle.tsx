import React, { useState, useEffect } from 'react';

import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, InputProps } from './Input';

import { InputCheckboxProps, InputCheckbox } from './InputCheckbox';
import tailwindConfig from '../../../tailwind.config';

interface InputToggleProps extends InputCheckboxProps {}

function InputToggle({
  state,
  setState,
  showValidity = false,
  ...rest
}: InputToggleProps) {
  return (
    <div className="flex flex-row items-center space-x-2">
      <div
        onClick={() => setState({ ...state, value: !state.value })}
        className="rounded-full p-1 surface border-[1px] "
        style={{ height: '1.5rem', width: '3rem', position: 'relative' }}
      >
        <div
          className={`rounded-full ${
            state.value ? 'bg-color-primary' : 'bg-color-invert'
          } h-full aspect-square`}
          style={{
            transform: state.value ? 'translateX(1.5rem)' : 'translateX(0)',
            transition: '0.1s',
          }}
        ></div>
        <div className="opacity-0 absolute">
          <InputCheckbox
            state={state}
            setState={setState}
            {...rest}
            showValidity={false}
          />
        </div>
      </div>
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputToggle };
