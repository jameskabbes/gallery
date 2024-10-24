import React from 'react';
import { InputCheckboxBase, InputCheckboxBaseProps } from './InputCheckboxBase';
import { Checkbox1 } from '../Utils/Checkbox';
import { CheckOrX } from './CheckOrX';

interface InputCheckboxProps extends InputCheckboxBaseProps {
  showValidity?: boolean;
}

function InputCheckbox({
  state,
  setState,
  showValidity = false,
  ...rest
}: InputCheckboxProps) {
  return (
    <div className="relative flex flex-row items-center space-x-2">
      <Checkbox1
        state={state.value}
        onClick={() => setState((prev) => ({ ...prev, value: !prev.value }))}
      >
        <InputCheckboxBase
          state={state}
          setState={setState}
          {...rest}
          className="absolute inset-0 opacity-0"
        />
      </Checkbox1>
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputCheckbox, InputCheckboxProps };
