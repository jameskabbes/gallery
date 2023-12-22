import React from 'react';
import { Photo } from '../../types';

function Image({
  photo,
  className = '',
}: {
  photo: Photo;
  className?: string;
}): JSX.Element {
  return <img className={className} src={photo.src.large} alt={photo.alt} />;
}

export { Image };
