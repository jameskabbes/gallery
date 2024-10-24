import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledRadioButton = createStyledSurfaceComponentCreator<
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

function RadioButton1({ children, state, ...rest }: CheckboxProps) {
  return (
    <RadioButtonBase {...rest}>
      <div
        className={`h-full w-full rounded-full ${
          state && 'bg-primary-light dark:bg-primary-light'
        } `}
        style={{
          transition: '0.1s',
        }}
      >
        {children}
      </div>
    </RadioButtonBase>
  );
}

export { RadioButton1, createStyledRadioButton };
