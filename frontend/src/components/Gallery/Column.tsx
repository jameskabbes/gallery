import React from 'react';
import { Photo } from '../../types';
import { GalleryView } from '../Photo/GalleryView';

function Column({
  photos,
  photoInds,
  setImagePreviewIndex,
}: {
  photos: Photo[];
  photoInds: number[];
  setImagePreviewIndex: CallableFunction;
}) {
  return (
    <>
      <div className="column">
        {photoInds.map((photoInd, i) => (
          <GalleryView
            key={i}
            photo={photos[photoInd]}
            index={photoInd}
            setImagePreviewIndex={setImagePreviewIndex}
          />
        ))}
      </div>
    </>
  );
}

export { Column };
