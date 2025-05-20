import React from 'react';
import createStyledSurfaceComponentCreator from '../../utils/createStyledSurfaceComponent';

export const createStyledCard = createStyledSurfaceComponentCreator<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>('div');

export const createStyledCardButton = createStyledSurfaceComponentCreator<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>('button');

export const Card1 = createStyledCard('rounded-2xl border-[1px] p-2');
export const CardButton = createStyledCardButton(
  'rounded-2xl border-[1px] p-2'
);
