import React from 'react';
import { Photo as PhotoType } from '../../types';

function GalleryView({
  photo,
  index = null,
}: {
  photo: PhotoType;
  index?: number | null;
}): JSX.Element {
  return (
    <div className="card flex items-center justify-center">
      <div className="relative">
        <img className="" src={photo.src.large} alt={photo.alt} />
        <div className="absolute inset-0 flex">
          <h2 className="text-white mx-3 my-2">{index}</h2>
        </div>
      </div>
    </div>
  );
}

export { GalleryView };
