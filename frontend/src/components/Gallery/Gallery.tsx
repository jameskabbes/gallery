import React, { useState, useEffect } from 'react';
import { Photo, Gallery } from '../../types';
import { PreviewView } from '../Photo/PreviewView';
import { getAspectRatio } from '../Photo/utils';
import { Column } from './Column';

function calculateNColumns(screenWidth: number): number {
  if (screenWidth < 300) {
    return 1;
  } else if (screenWidth < 600) {
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
    gallery[minIndex].push(index);
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
    if (nColumns !== null) {
      setColumns(dividePhotosToColumns(photos, nColumns));
    }
  }, [nColumns]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setImagePreviewIndex(null);
      } else if (event.key === 'ArrowLeft') {
        if (imagePreviewIndex !== null) {
          let ind = (imagePreviewIndex - 1) % photos.length;
          while (ind < 0) {
            ind += photos.length;
          }
          setImagePreviewIndex(ind);
        }
      } else if (event.key === 'ArrowRight') {
        if (imagePreviewIndex !== null) {
          setImagePreviewIndex((imagePreviewIndex + 1) % photos.length);
        }
      }
    };

    // Add the event listener when the component mounts
    document.addEventListener('keydown', handleKeyDown);

    // Remove the event listener when the component unmounts
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [imagePreviewIndex]); // Ensure to include any dependencies in the dependency array

  return (
    <>
      {columns !== null && nColumns !== null && (
        <>
          {imagePreviewIndex !== null && (
            <div>
              <div
                className="fixed top-0 left-0 w-full h-full flex items-center justify-center z-10"
                onClick={() => setImagePreviewIndex(null)}
              >
                <div className="absolute top-0 left-0 w-full h-full bg-gray-300/50"></div>
                <div className="relative z-20">
                  <PreviewView
                    photo={photos[imagePreviewIndex]}
                    setImagePreviewIndex={setImagePreviewIndex}
                  />
                </div>
              </div>
            </div>
          )}
          <div className="gallery">
            {columns.map((column, columnInd) => (
              <Column
                key={columnInd}
                photos={photos}
                photoInds={column}
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
