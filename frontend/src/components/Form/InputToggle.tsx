import React, { useState, useEffect } from 'react';

import { InputCheckboxBase, InputCheckboxBaseProps } from './InputCheckboxBase';
import { Checkbox1 } from '../Utils/Checkbox';
import { CheckOrX } from './CheckOrX';
import { Toggle1 } from '../Utils/Toggle';

interface InputToggleProps extends InputCheckboxBaseProps {
  showValidity?: boolean;
}

function InputToggle({
  state,
  setState,
  showValidity = false,
  ...rest
}: InputToggleProps) {
  return (
    <div className="flex flex-row items-center space-x-2">
      <Toggle1
        state={state.value}
        onClick={() => setState((prev) => ({ ...prev, value: !prev.value }))}
      />
      {showValidity && (
        <span title={state.error || ''}>
          <CheckOrX status={state.status} />
        </span>
      )}
    </div>
  );
}

export { InputToggle };
