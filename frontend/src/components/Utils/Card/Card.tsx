import React from 'react';
import { UtilPatternProps } from '../../../types';
import { Surface } from '../Surface';

type CardProps = UtilPatternProps<'div'>;

function Card({ children, className = '', ...rest }: CardProps) {
  return (
    <Surface>
      <div className={`rounded-2xl border-[1px] p-2 ${className}`} {...rest}>
        {children}
      </div>
    </Surface>
  );
}

export default Card;
export { CardProps };
