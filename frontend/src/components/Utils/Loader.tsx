import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledLoader = createStyledSurfaceComponentCreator<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>('span');

const LoaderBase = createStyledLoader('loader-base');
const Loader1 = createStyledLoader('loader1');
const Loader2 = createStyledLoader('loader2');
const Loader3 = createStyledLoader('loader3');

export { LoaderBase, Loader1, Loader2, Loader3, createStyledLoader };
