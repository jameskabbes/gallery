import React, { useEffect } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

function PreviewView({
  photo,
  setImagePreviewIndex,
}: {
  photo: Photo;
  setImagePreviewIndex: CallableFunction;
}) {
  return (
    <>
      <div className="flex flex-col card">
        <h2>{photo.id}</h2>
        <button onClick={() => setImagePreviewIndex(null)}>Close</button>
        <Image photo={photo} />
      </div>
    </>
  );
}

export { PreviewView };
