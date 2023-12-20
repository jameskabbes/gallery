import React from 'react';
import { Photo as PhotoType } from '../../types';

function Photo({ photo }: { photo: PhotoType }): JSX.Element {
  return (
    <div className="mx-auto">
      <div className="card flex items-center justify-center">
        <img className="" src={photo.src.large} alt={photo.alt} />
      </div>
    </div>
  );
}

export { Photo };
