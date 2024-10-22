import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledLoader = createStyledSurfaceComponentCreator<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>('span');

const Loader1 = createStyledLoader('loader-base loader1');
const Loader2 = createStyledLoader('loader-base loader2');

export { Loader1, Loader2, createStyledLoader };
