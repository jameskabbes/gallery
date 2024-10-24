import React from 'react';
import { CheckOrX } from './CheckOrX';
import { InputState } from '../../types';
import { InputTextBase, InputTextBaseProps } from './InputTextBase';
import { Surface } from '../Utils/Surface';

interface InputTextProps extends InputTextBaseProps {
  showValidity?: boolean;
}

function InputText({
  state,
  setState,
  showValidity = true,
  ...rest
}: InputTextProps) {
  return (
    <Surface>
      <div className="flex flex-row items-center space-x-2 input-text-container">
        <InputTextBase state={state} setState={setState} {...rest} />
        <div className="flex-1">
          {showValidity && (
            <span title={state.error || ''}>
              <CheckOrX status={state.status} />
            </span>
          )}
        </div>
      </div>
    </Surface>
  );
}

export { InputText, InputTextProps };
