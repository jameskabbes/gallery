import React, { useState, useEffect } from 'react';

import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, InputProps } from './Input';

import { Toggle } from '../Utils/Toggle';

import { InputCheckboxProps, InputCheckbox } from './InputCheckbox';

interface InputToggleProps extends InputCheckboxProps {}

function InputToggle({ state, setState, ...rest }: InputToggleProps) {
  return (
    <div className="flex flex-row items-center space-x-2 input-checkbox">
      <div
        className="rounded-full p-1 component-bg-color border-2"
        style={{ height: '2rem', width: '4rem', position: 'relative' }}
      >
        <InputCheckbox
          state={state}
          setState={setState}
          className="rounded-full bg-primary h-full aspect-square transition-transform duration-100"
          style={{ transform: state ? 'translateX(2rem)' : 'translateX(0)' }}
          {...rest}
        />
      </div>
    </div>
  );
}

export { InputToggle };
