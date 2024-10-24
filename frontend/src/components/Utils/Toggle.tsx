import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledToggle = createStyledSurfaceComponentCreator<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>('div');

const Toggle1Base = createStyledToggle(
  'inline-block input-toggle-container rounded-full relative ',
  {
    style: {
      borderWidth: '0.0625em',
      width: '2em',
      height: '1em',
      padding: '0.15em',
    },
  }
);

interface ToggleProps extends React.HTMLAttributes<HTMLDivElement> {
  state: boolean;
}

function Toggle1({ children, state, ...rest }: ToggleProps) {
  return (
    <Toggle1Base {...rest}>
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
    </Toggle1Base>
  );
}

export { Toggle1, createStyledToggle };
