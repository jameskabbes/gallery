import { Photo } from '../../types';

export function getAspectRatio(photo: Photo) {
  return photo.width / photo.height;
}
