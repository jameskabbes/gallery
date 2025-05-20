import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

export const createStyledRadioButton = createStyledSurfaceComponentCreator<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>('div');

const RadioButtonBase = createStyledRadioButton(
  'input-radio-container rounded-full',
  {
    style: {
      borderWidth: '0.0625em',
      width: '1em',
      height: '1em',
      margin: '0',
      padding: '0.1em',
    },
  }
);

interface CheckboxProps extends React.HTMLAttributes<HTMLDivElement> {
  state: boolean;
}

export function RadioButton1({ children, state, ...rest }: CheckboxProps) {
  return (
    <RadioButtonBase {...rest}>
      <div
        className={`h-full w-full rounded-full ${state && 'bg-color-primary'} `}
        style={{
          transition: '0.1s',
        }}
      >
        {children}
      </div>
    </RadioButtonBase>
  );
}
