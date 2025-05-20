import React, { useState, useEffect, useReducer } from 'react';
import { PreviewView } from '../Photo/PreviewView';
import { getAspectRatio } from '../Photo/utils';
import { reducer as PreviewIndexReducer } from './PreviewIndexTracker';

// function calculateNColumns(screenWidth: number): number {
//   if (screenWidth < 300) {
//     return 1;
//   } else if (screenWidth < 700) {
//     return 2;
//   } else if (screenWidth < 1100) {
//     return 3;
//   } else if (screenWidth < 1600) {
//     return 4;
//   } else {
//     return 5;
//   }
// }

// function dividePhotosToColumns(photos: Photo[], nColumns: number): Gallery {
//   let gallery: Gallery = [];
//   for (let i = 0; i < nColumns; i++) {
//     gallery.push([]);
//   }

//   let columnHeights: number[] = Array(nColumns).fill(0.0);

//   photos.forEach((photo, index) => {
//     const minIndex = columnHeights.indexOf(Math.min(...columnHeights));
//     columnHeights[minIndex] += 1 / getAspectRatio(photo);

//     photo.index = index;
//     gallery[minIndex].push(index);
//   });

//   return gallery;
// }

// export function Gallery({ photos }: { photos: Photo[] }): JSX.Element {
//   const [screenWidth, setScreenWidth] = useState<number>(window.innerWidth);
//   const [nColumns, setNColumns] = useState<number>(null);
//   const [columns, setColumns] = useState<Gallery>(null);
//   const [imagePreviewIndex, imagePreviewIndexDispatch] = useReducer(
//     PreviewIndexReducer,
//     null
//   );

//   const handleResize = () => {
//     setScreenWidth(window.innerWidth);
//   };

//   useEffect(() => {
//     window.addEventListener('resize', handleResize);
//     return () => {
//       window.removeEventListener('resize', handleResize);
//     };
//   }, []);

//   useEffect(() => {
//     const newNColumns = calculateNColumns(screenWidth);
//     if (newNColumns !== nColumns) {
//       setNColumns(newNColumns);
//     }
//   }, [screenWidth, nColumns]);

//   useEffect(() => {
//     if (nColumns !== null) {
//       setColumns(dividePhotosToColumns(photos, nColumns));
//     }
//   }, [nColumns]);

//   useEffect(() => {
//     console.log(imagePreviewIndex);
//   }, [imagePreviewIndex]);

//   useEffect(() => {
//     const handleKeyDown = (event) => {
//       if (event.key === 'Escape') {
//         imagePreviewIndexDispatch({ type: 'SET_NULL' });
//       } else if (event.key === 'ArrowLeft') {
//         imagePreviewIndexDispatch({
//           type: 'DECREMENT',
//           nPhotos: photos.length,
//         });
//       } else if (event.key === 'ArrowRight') {
//         imagePreviewIndexDispatch({
//           type: 'INCREMENT',
//           nPhotos: photos.length,
//         });
//       }
//     };

//     // Add the event listener when the component mounts
//     document.addEventListener('keydown', handleKeyDown);

//     // Remove the event listener when the component unmounts
//     return () => {
//       document.removeEventListener('keydown', handleKeyDown);
//     };
//   }, [imagePreviewIndex]); // Ensure to include any dependencies in the dependency array

//   return (
//     <>
//       {columns !== null && nColumns !== null && (
//         <>
//           {imagePreviewIndex !== null && (
//             <PreviewView
//               photo={photos[imagePreviewIndex]}
//               nPhotos={photos.length}
//               imagePreviewIndexDispatch={imagePreviewIndexDispatch}
//             />
//           )}
//           <div
//             className={`gallery ${
//               imagePreviewIndex !== null ? 'blur-[2px]' : ''
//             }`}
//           >
//             {columns.map((column, columnInd) => (
//               <Column
//                 key={columnInd}
//                 photos={photos}
//                 photoInds={column}
//                 imagePreviewIndexDispatch={imagePreviewIndexDispatch}
//               />
//             ))}
//           </div>
//         </>
//       )}
//     </>
//   );
// }
