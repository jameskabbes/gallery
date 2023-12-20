import React, { useState, useEffect } from 'react';
import { Photo, Gallery } from '../../types';
import { GalleryView } from '../Photo/GalleryView';

function calculateNColumns(screenWidth: number): number {
  if (screenWidth < 600) {
    return 2;
  } else if (screenWidth < 1200) {
    return 3;
  } else if (screenWidth < 2000) {
    return 4;
  } else {
    return 5;
  }
}

function dividePhotosToColumns(photos: Photo[], nColumns: number): Gallery {
  let gallery: Gallery = Array.from({ length: nColumns }, () => []);

  photos.forEach((photo, index) => {
    const columnIndex = index % nColumns;
    photo.index = index;
    gallery[columnIndex].push(photo);
  });

  return gallery;
}

function Gallery({ photos }: { photos: Photo[] }): JSX.Element {
  const [screenWidth, setScreenWidth] = useState<number>(window.innerWidth);
  const [nColumns, setNColumns] = useState<number>(
    calculateNColumns(screenWidth)
  );
  const [galleryColumns, setGalleryColumns] = useState<Gallery>(
    dividePhotosToColumns(photos, nColumns)
  );

  const [imagePreviewIndex, setImagePreviewIndex] = useState(null);

  const handleResize = () => {
    setScreenWidth(window.innerWidth);
  };

  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    const newNColumns = calculateNColumns(screenWidth);
    if (newNColumns !== nColumns) {
      setNColumns(newNColumns);
    }
  }, [screenWidth, nColumns]);

  useEffect(() => {
    setGalleryColumns(dividePhotosToColumns(photos, nColumns));
  }, [nColumns]);

  return (
    <>
      {imagePreviewIndex && (
        <div>
          <div className="fixed top-0 left-0 w-full h-full bg-color-darker bg-opacity-50 z-10"></div>
          <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center z-20">
            <div className="bg-white p-6 rounded-lg">
              <GalleryView photo={photos[imagePreviewIndex]} />
              <button onClick={() => setImagePreviewIndex(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-row justify-around">
        {galleryColumns.map((columnPhotos, columnInd) => (
          <div key={columnInd} className="column">
            <div>
              {columnPhotos.map((photo, index) => (
                <button onClick={() => setImagePreviewIndex(photo.index)}>
                  <GalleryView key={index} photo={photo} index={photo.index} />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export { Gallery };
