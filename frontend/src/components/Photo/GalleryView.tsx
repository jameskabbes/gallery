import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

function GalleryView({
  photo,
  index,
  setImagePreviewIndex,
}: {
  photo: Photo;
  index: number;
  setImagePreviewIndex: CallableFunction;
}): JSX.Element {
  return (
    <button onClick={() => setImagePreviewIndex(index)}>
      <div className="flex items-center justify-center">
        <div className="img-card relative">
          <Image photo={photo} />
          <div className="absolute inset-0 flex">
            <h3 className="text-white mx-3 my-2">{index}</h3>
          </div>
        </div>
      </div>
    </button>
  );
}

export { GalleryView };
