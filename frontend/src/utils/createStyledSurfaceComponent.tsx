import React, { forwardRef, ElementType, HTMLAttributes } from 'react';
import { Surface } from '../components/Utils/Surface';

function createStyledSurfaceComponentCreator<
  T extends HTMLElement,
  ComponentProps extends HTMLAttributes<any>
>(Tag: ElementType) {
  function createStyledSurfaceComponent(
    baseClassName: string,
    defaultProps?: Partial<ComponentProps>
  ) {
    return forwardRef<T, ComponentProps>(
      ({ children, className = '', ...rest }, ref) => {
        return (
          <Surface>
            <Tag
              className={`${baseClassName} ${className}`}
              {...defaultProps}
              {...rest}
              ref={ref}
            >
              {children}
            </Tag>
          </Surface>
        );
      }
    );
  }
  return createStyledSurfaceComponent; // Ensure the function is returned
}

export default createStyledSurfaceComponentCreator;
