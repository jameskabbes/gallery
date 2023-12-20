import { Photo as PhotoPexels } from 'pexels';

interface Photo extends PhotoPexels {
  index?: number;
}

type Gallery = Photo[][];

export { Photo, Gallery };
