import React, { forwardRef } from 'react';
import { Surface } from './Surface';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, className = '', ...rest }, ref) => {
    return (
      <Surface>
        <button ref={ref} className={`button-base ${className}`} {...rest}>
          {children}
        </button>
      </Surface>
    );
  }
);

const createStyledButton = (baseClassName: string) => {
  return forwardRef<HTMLButtonElement, ButtonProps>(
    ({ children, className = '', ...rest }, ref) => {
      return (
        <Button ref={ref} className={`${baseClassName} ${className}`} {...rest}>
          {children}
        </Button>
      );
    }
  );
};

const Button1 = createStyledButton(
  'bg-primary-light dark:bg-primary-dark text-light-lighter'
);
const Button2 = createStyledButton('button-base border-[1px]');
const Button3 = createStyledButton(
  'button-base bg-color-invert text-color-invert'
);

const ButtonSubmit = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, className = '', ...rest }, ref) => {
    return (
      <Button1
        ref={ref}
        type="submit"
        className={`flex flex-row justify-center p-4 rounded-3xl mb-0 ${className}`}
        {...rest}
      >
        {children}
      </Button1>
    );
  }
);

export default Button;
export { ButtonProps, Button1, Button2, Button3, ButtonSubmit };
