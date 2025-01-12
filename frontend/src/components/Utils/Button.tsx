import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledButton = createStyledSurfaceComponentCreator<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>('button');

const Button1Base = createStyledButton('button1');
const Button2Base = createStyledButton('button2');
const Button3Base = createStyledButton('button3');
const ButtonSubmitBase = createStyledButton('button-submit', {
  type: 'submit',
});

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isActive?: boolean;
}

function Button1({ children, isActive, ...rest }: ButtonProps) {
  return (
    <Button1Base {...rest} className={`${rest.className} }`}>
      {children}
    </Button1Base>
  );
}

function Button2({ children, isActive, ...rest }: ButtonProps) {
  return (
    <Button2Base
      {...rest}
      className={`${rest.className} ${
        isActive ? 'border-primary-light dark:border-primary-dark' : ''
      } hover:border-primary-light dark:hover:border-primary-dark`}
    >
      {children}
    </Button2Base>
  );
}

function Button3({ children, isActive, ...rest }: ButtonProps) {
  return (
    <Button3Base
      {...rest}
      className={`${rest.className} ${
        isActive ? 'border-primary-light dark:border-primary-dark' : ''
      }`}
    >
      {children}
    </Button3Base>
  );
}

function ButtonSubmit({ children, isActive, ...rest }: ButtonProps) {
  return (
    <ButtonSubmitBase
      {...rest}
      className={`${rest.className} ${
        isActive ? 'border-primary-light dark:border-primary-dark' : ''
      }`}
    >
      {children}
    </ButtonSubmitBase>
  );
}

export { Button1, Button2, Button3, ButtonSubmit, createStyledButton };
