import React from 'react';
import { Photo as PhotoType } from '../../types';
import { Photo } from './Photo';

function Photos({ photos }: { photos: PhotoType[] }): JSX.Element {
  return (
    <div className="photos">
      {photos.map((photo, index) => (
        <Photo key={index} photo={photo} />
      ))}
    </div>
  );
}

export { Photos };
