import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';

function Image({ photo }: { photo: Photo }): JSX.Element {
  return <img src={photo.src.medium} alt={photo.alt} />;
}

export { Image };
