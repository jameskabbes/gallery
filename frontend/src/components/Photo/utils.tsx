import { Photo } from '../../types';

function getAspectRatio(photo: Photo) {
  return photo.width / photo.height;
}

export { getAspectRatio };
