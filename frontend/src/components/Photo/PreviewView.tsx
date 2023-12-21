import React, { useEffect } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

import { IoIosArrowForward, IoIosArrowBack, IoIosClose } from 'react-icons/io';

function PreviewView({
  photo,
  nPhotos,
  imagePreviewIndexDispatch,
}: {
  photo: Photo;
  nPhotos: number;
  imagePreviewIndexDispatch: CallableFunction;
}) {
  return (
    <>
      <div className="bg-color-darker relative">
        <Image photo={photo} />

        <button
          className="absolute inset-0 flex justify-end"
          onClick={() => {
            imagePreviewIndexDispatch({ type: 'SET_NULL' });
          }}
        >
          <h1>
            <IoIosClose />
          </h1>
        </button>
        <button
          className="absolute inset-0 flex-col justify-center"
          onClick={() => {
            imagePreviewIndexDispatch({ type: 'DECREMENT', nPhotos: nPhotos });
          }}
        >
          <h1>
            <IoIosArrowBack />
          </h1>
        </button>
        <button
          onClick={() => {
            imagePreviewIndexDispatch({ type: 'INCREMENT', nPhotos: nPhotos });
          }}
        >
          <h1>
            <IoIosArrowForward />
          </h1>
        </button>
      </div>
    </>
  );
}

export { PreviewView };
