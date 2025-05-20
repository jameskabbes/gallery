import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

export const createStyledCheckbox = createStyledSurfaceComponentCreator<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>('div');

const Checkbox1Base = createStyledCheckbox(
  'relative input-checkbox-container',
  {
    style: {
      borderRadius: '0.25em',
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

export function Checkbox1({ children, state, ...rest }: CheckboxProps) {
  return (
    <Checkbox1Base {...rest}>
      <div
        className={`h-full ${state ? 'bg-color-primary' : ''}`}
        style={{
          transition: '0.1s',
          borderRadius: '0.15em',
        }}
      >
        {children}
      </div>
    </Checkbox1Base>
  );
}
