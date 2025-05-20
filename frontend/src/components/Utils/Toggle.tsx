import React, { forwardRef } from 'react';
import { Surface } from './Surface';

export interface ToggleProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  state: boolean;
  disabled?: boolean;
}

function Toggle1Creator() {
  return forwardRef<HTMLButtonElement, ToggleProps>(
    ({ children, state, disabled = false, className = '', ...rest }, ref) => {
      return (
        <Surface>
          <button
            ref={ref}
            className={`inline-block input-toggle-container rounded-full relative ${
              disabled ? 'opacity-50 pointer-events-none' : ''
            }`}
            style={{
              borderWidth: '0.0625em',
              width: '2em',
              height: '1em',
              padding: '0.15em',
            }}
            disabled={disabled}
            {...rest}
          >
            <div
              className={`rounded-full ${
                state ? 'bg-color-primary' : 'bg-color-invert'
              } h-full aspect-square`}
              style={{
                transform: state ? 'translateX(1em)' : 'translateX(0)',
                transition: '0.1s',
              }}
            >
              {children}
            </div>
          </button>
        </Surface>
      );
    }
  );
}

export const Toggle1 = Toggle1Creator();
