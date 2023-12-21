import React, { useEffect } from 'react';
import { Photo } from '../../types';
import { Image } from './Image';

import {
  IoIosArrowForward,
  IoIosArrowBack,
  IoIosExit,
  IoIosClose,
} from 'react-icons/io';

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
      <h1>
        <IoIosClose
          onClick={() => {
            imagePreviewIndexDispatch({ type: 'SET_NULL' });
          }}
        />
      </h1>
      <h1
        onClick={() => {
          imagePreviewIndexDispatch({ type: 'INCREMENT', nPhotos: nPhotos });
        }}
      >
        <IoIosArrowBack />
      </h1>
      <h1>
        <IoIosArrowForward
          onClick={() => {
            imagePreviewIndexDispatch({ type: 'DECREMENT', nPhotos: nPhotos });
          }}
        />
      </h1>
      <Image photo={photo} />
    </>
  );
}

export { PreviewView };
