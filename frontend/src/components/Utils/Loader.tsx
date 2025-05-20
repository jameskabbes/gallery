import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

export const createStyledLoader = createStyledSurfaceComponentCreator<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>('span');

export const LoaderBase = createStyledLoader('loader-base');
export const Loader1 = createStyledLoader('loader1');
export const Loader2 = createStyledLoader('loader2');
export const Loader3 = createStyledLoader('loader3');
