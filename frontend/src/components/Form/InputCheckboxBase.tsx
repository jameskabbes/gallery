import React, { useState, useEffect } from 'react';
import { CheckOrX } from './CheckOrX';
import { Surface } from '../Utils/Surface';
import { BaseInputProps, Input, InputProps } from './Input';
import { Checkbox1 } from '../Utils/Checkbox';

type T = boolean;

interface InputCheckboxBaseProps extends BaseInputProps<T> {}

function InputCheckboxBase({
  state,
  setState,
  ...rest
}: InputCheckboxBaseProps) {
  return (
    <Input
      state={state}
      setState={setState}
      checked={state.value}
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        setState({
          ...state,
          value: e.target.checked,
        });
      }}
      type={'checkbox'}
      {...rest}
    />
  );
}

export { InputCheckboxBase, InputCheckboxBaseProps };
