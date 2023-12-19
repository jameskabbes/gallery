import React from 'react';
import { Photo as PhotoType } from '../../types';

function Photo({ photo }: { photo: PhotoType }): JSX.Element {
  return (
    <div className="photo">
      <img src={photo.src.medium} alt={photo.alt} />
    </div>
  );
}

export { Photo };
