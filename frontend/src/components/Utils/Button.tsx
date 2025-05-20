import React, { forwardRef } from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

export const createStyledButton = createStyledSurfaceComponentCreator<
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

export const Button1 = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, isActive, className = '', ...rest }, ref) => {
    return (
      <Button1Base ref={ref} {...rest} className={`${className}`}>
        {children}
      </Button1Base>
    );
  }
);

export const Button2 = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, isActive, className = '', ...rest }, ref) => {
    return (
      <Button2Base
        ref={ref}
        {...rest}
        className={`${className} ${
          isActive ? 'border-primary-light dark:border-primary-dark' : ''
        } hover:border-primary-light dark:hover:border-primary-dark`}
      >
        {children}
      </Button2Base>
    );
  }
);

export const Button3 = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, isActive, className = '', ...rest }, ref) => {
    return (
      <Button3Base
        ref={ref}
        {...rest}
        className={`${className} ${
          isActive ? 'border-primary-light dark:border-primary-dark' : ''
        }`}
      >
        {children}
      </Button3Base>
    );
  }
);

export const ButtonSubmit = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, isActive, className = '', ...rest }, ref) => {
    return (
      <ButtonSubmitBase ref={ref} {...rest} className={`${className} `}>
        {children}
      </ButtonSubmitBase>
    );
  }
);
