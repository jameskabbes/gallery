import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledButton = createStyledSurfaceComponentCreator<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>('button');

const Button1 = createStyledButton(
  'button-base bg-color-primary text-light-lighter'
);
const Button2 = createStyledButton('button-base border-[1px]');
const Button3 = createStyledButton(
  'button-base bg-color-invert text-color-invert'
);

const ButtonSubmit = createStyledButton(
  'button-base bg-color-primary text-light-lighter flex flex-row justify-center p-4 rounded-3xl mb-0',
  { type: 'submit' }
);

export { Button1, Button2, Button3, ButtonSubmit, createStyledButton };
