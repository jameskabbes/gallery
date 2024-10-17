import React, { useState, useEffect } from 'react';

import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { BaseInputProps, Input, InputProps } from './Input';

type T = boolean;

interface InputCheckboxProps extends BaseInputProps<T> {
  showValidity?: boolean;
}

function InputCheckbox({
  state,
  setState,
  showValidity = true,
  ...rest
}: InputCheckboxProps) {
  return (
    <div className="flex flex-row items-center space-x-2 input-checkbox">
      <Input
        state={state}
        setState={setState}
        checked={state.value}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          let newValue: InputCheckboxProps['state']['value'] = e.target.checked;
          setState({
            ...state,
            value: newValue,
          });
        }}
        {...rest}
      />
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputCheckbox };
