import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

function GalleryView({
  photo,
  setImagePreviewIndex,
}: {
  photo: Photo;
  setImagePreviewIndex: CallableFunction;
}): JSX.Element {
  useEffect(() => {
    console.log(photo.index);
  }, []);

  return (
    <div className="flex items-center justify-center">
      <button onClick={() => setImagePreviewIndex(photo.index)}>
        <div className="img-card">
          <div className="relative">
            <Image photo={photo} />
            <div className="absolute inset-0 flex">
              <h2 className="text-white mx-3 my-2">{photo.index}</h2>
            </div>
          </div>
        </div>
      </button>
    </div>
  );
}

export { GalleryView };
