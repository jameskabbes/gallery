import React, { useEffect } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

import { IoIosArrowForward, IoIosArrowBack, IoIosClose } from 'react-icons/io';

export function PreviewView({
  photo,
  nPhotos,
  imagePreviewIndexDispatch,
}: {
  photo: Photo;
  nPhotos: number;
  imagePreviewIndexDispatch: CallableFunction;
}) {
  return (
    <div
      className="fixed top-0 left-0 h-screen w-screen flex items-center justify-center z-10"
      onClick={() => {
        imagePreviewIndexDispatch({ type: 'SET_NULL' });
      }}
    >
      <div
        className="absolute mx-auto w-5/6 h-5/6 bg-color-lighter bg-opacity-t75 rounded-lg z-20"
        onClick={(event) => {
          event.stopPropagation();
        }}
      >
        <div className="flex flex-row h-full justify-between">
          <div className="flex flex-col justify-center">
            <button
              onClick={() => {
                imagePreviewIndexDispatch({
                  type: 'DECREMENT',
                  nPhotos: nPhotos,
                });
              }}
            >
              <h1 className="mb-0">
                <IoIosArrowBack />
              </h1>
            </button>
          </div>
          <div className="flex-row items-center">
            <Image photo={photo} className="img-preview-view" />
          </div>
          <div className="flex flex-col justify-center">
            <div className="absolute top-0">
              <button
                onClick={() => {
                  imagePreviewIndexDispatch({
                    type: 'SET_NULL',
                  });
                }}
              >
                <h1 className="mb-0">
                  <IoIosClose />
                </h1>
              </button>
            </div>

            <button
              onClick={() => {
                imagePreviewIndexDispatch({
                  type: 'INCREMENT',
                  nPhotos: nPhotos,
                });
              }}
            >
              <h1 className="mb-0">
                <IoIosArrowForward />
              </h1>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
