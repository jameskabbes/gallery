import React, { useState, useEffect } from 'react';
import { Photo, Gallery } from '../../types';
import { PreviewView } from '../Photo/PreviewView';
import { getAspectRatio } from '../Photo/utils';
import { Column } from './Column';

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
  let gallery: Gallery = [];
  for (let i = 0; i < nColumns; i++) {
    gallery.push([]);
  }

  let columnHeights: number[] = Array(nColumns).fill(0.0);

  photos.forEach((photo, index) => {
    const minIndex = columnHeights.indexOf(Math.min(...columnHeights));
    columnHeights[minIndex] += 1 / getAspectRatio(photo);

    photo.index = index;
    gallery[minIndex].push(photo);
  });

  return gallery;
}

function Gallery({ photos }: { photos: Photo[] }): JSX.Element {
  const [screenWidth, setScreenWidth] = useState<number>(window.innerWidth);
  const [nColumns, setNColumns] = useState<number>(null);
  const [columns, setColumns] = useState<Gallery>(null);
  const [imagePreviewIndex, setImagePreviewIndex] = useState(null);

  const handleResize = () => {
    setScreenWidth(window.innerWidth);
  };

  useEffect(() => {
    console.log('resizing');
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    console.log('calculating nColumns');
    const newNColumns = calculateNColumns(screenWidth);
    if (newNColumns !== nColumns) {
      setNColumns(newNColumns);
    }
  }, [screenWidth, nColumns]);

  useEffect(() => {
    if (nColumns !== null) {
      setColumns(dividePhotosToColumns(photos, nColumns));
    }
  }, [nColumns]);

  return (
    <>
      {columns !== null && nColumns !== null && (
        <>
          {imagePreviewIndex && (
            <div>
              <div className="fixed top-0 left-0 w-full h-full bg-opacity-50 z-10"></div>
              <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center z-20">
                <PreviewView
                  photo={photos[imagePreviewIndex]}
                  setImagePreviewIndex={setImagePreviewIndex}
                />
              </div>
            </div>
          )}
          <div className="gallery">
            {columns.map((column, columnInd) => (
              <Column
                key={columnInd}
                photos={column}
                setImagePreviewIndex={setImagePreviewIndex}
              />
            ))}
          </div>
        </>
      )}
    </>
  );
}

export { Gallery };
