import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

export function GalleryView({
  photo,
  index,
  imagePreviewIndexDispatch,
}: {
  photo: Photo;
  index: number;
  imagePreviewIndexDispatch: CallableFunction;
}): JSX.Element {
  const [showIndex, setShowIndex] = useState(true);
  return (
    <div
      className="flex items-center justify-center"
      onMouseEnter={() => {
        setShowIndex(false);
      }}
      onMouseLeave={() => {
        setShowIndex(true);
      }}
      onClick={() =>
        imagePreviewIndexDispatch({ type: 'SET_VALUE', value: index })
      }
    >
      <div className="img-card relative">
        <Image photo={photo} className="img-gallery-view" />
        <div className="absolute inset-0 flex">
          {showIndex && <h3 className="text-white mx-3 my-2">{index}</h3>}
        </div>
      </div>
    </div>
  );
}
