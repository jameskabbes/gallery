import React from 'react';
import { Photo } from '../../types';
import { GalleryView } from '../Photo/GalleryView';

function Column({
  photos,
  setImagePreviewIndex,
}: {
  photos: Photo[];
  setImagePreviewIndex: CallableFunction;
}) {
  return (
    <>
      <div className="column">
        {photos.map((photo, index) => (
          <GalleryView
            key={index}
            photo={photo}
            setImagePreviewIndex={setImagePreviewIndex}
          />
        ))}
      </div>
    </>
  );
}

export { Column };
