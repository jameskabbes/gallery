import React, { forwardRef } from 'react';
import { Surface } from '../Surface';

type CardProps = React.HTMLAttributes<HTMLDivElement>;

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, className = '', ...rest }, ref) => {
    return (
      <Surface>
        <div
          ref={ref}
          className={`rounded-2xl border-[1px] p-2 ${className}`}
          {...rest}
        >
          {children}
        </div>
      </Surface>
    );
  }
);

export default Card;
export { CardProps };
