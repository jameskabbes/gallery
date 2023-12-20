import React, { useState, useEffect, SetStateAction } from 'react';
import { Photo as PhotoType } from '../../types';
import { Photo } from '../Photo/Photo';

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

function dividePhotosToColumns(
  photos: PhotoType[],
  nColumns: number
): PhotoType[][] {
  let gallery: PhotoType[][] = Array.from({ length: nColumns }, () => []);

  photos.forEach((photo, index) => {
    const columnIndex = index % nColumns;
    gallery[columnIndex].push(photo);
  });

  return gallery;
}

function Gallery({ photos }: { photos: PhotoType[] }): JSX.Element {
  const [screenWidth, setScreenWidth] = useState<number>(window.innerWidth);
  const [nColumns, setNColumns] = useState<number>(
    calculateNColumns(screenWidth)
  );
  const [galleryColumns, setGalleryColumns] = useState<PhotoType[][]>(
    dividePhotosToColumns(photos, nColumns)
  );

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
      <div className="flex flex-row justify-around">
        {galleryColumns.map((columnPhotos, columnInd) => (
          <div key={columnInd} className="column">
            <div>
              {columnPhotos.map((photo, index) => (
                <Photo key={index} photo={photo} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export { Gallery };
