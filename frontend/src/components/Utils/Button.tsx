import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledButton = createStyledSurfaceComponentCreator<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>('button');

const Button1 = createStyledButton('button1');
const Button2 = createStyledButton('button2');
const Button3 = createStyledButton('button3');

const ButtonSubmit = createStyledButton('button-submit', { type: 'submit' });

export { Button1, Button2, Button3, ButtonSubmit, createStyledButton };
