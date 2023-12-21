import React, { useEffect } from 'react';
import { Photo } from '../../types';
import { Card } from './Card';

function PreviewView({
  photo,
  setImagePreviewIndex,
}: {
  photo: Photo;
  setImagePreviewIndex: CallableFunction;
}) {
  useEffect(() => {
    console.log(photo);
  }, []);

  return (
    <>
      <div className="flex flex-col card">
        <button onClick={() => setImagePreviewIndex(null)}>Close</button>
        <Card photo={photo} />
      </div>
    </>
  );
}

export { PreviewView };
