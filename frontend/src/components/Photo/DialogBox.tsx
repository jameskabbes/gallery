import React from 'react';
import { Photo } from '../../types';
import { GalleryView } from './GalleryView';

function DialogBox({ photo }: { photo: Photo }) {
  return (
    <div className="card">
      <GalleryView photo={photo} />
    </div>
  );
}

export { DialogBox };
