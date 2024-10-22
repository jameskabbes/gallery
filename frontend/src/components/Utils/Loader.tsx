import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledLoader = createStyledSurfaceComponentCreator<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>('span');

const Loader1 = createStyledLoader('base-loader loader1');
const Loader2 = createStyledLoader('base-loader loader2');

export { Loader1, Loader2, createStyledLoader };
