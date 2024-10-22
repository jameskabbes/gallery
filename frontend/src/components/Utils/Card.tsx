import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

const createStyledCard = createStyledSurfaceComponentCreator<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>('div');

const Card1 = createStyledCard('rounded-2xl border-[1px] p-2');

export { Card1, createStyledCard };
