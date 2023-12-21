import React, { useEffect, useState } from 'react';
import { Photo } from '../../types';

function Card({
  photo,
  showIndex = true,
}: {
  photo: Photo;
  showIndex?: boolean;
}): JSX.Element {
  return (
    <>
      <div className="relative">
        <img className="" src={photo.src.medium} alt={photo.alt} />
        {showIndex && (
          <div className="absolute inset-0 flex">
            <h2 className="text-white mx-3 my-2">{photo.index}</h2>
          </div>
        )}
      </div>
    </>
  );
}

export { Card };
