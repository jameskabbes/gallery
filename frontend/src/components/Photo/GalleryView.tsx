import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';
import { Card } from './Card';

function GalleryView({
  photo,
  setImagePreviewIndex,
}: {
  photo: Photo;
  setImagePreviewIndex: CallableFunction;
  index?: number | null;
}): JSX.Element {
  return (
    <div className="flex items-center justify-center">
      <button onClick={() => setImagePreviewIndex(photo.index)}>
        <div className="img-card">
          <Card photo={photo} />
        </div>
      </button>
    </div>
  );
}

export { GalleryView };
