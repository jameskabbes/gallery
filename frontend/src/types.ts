import { Photo as PhotoPexels } from 'pexels';

interface Photo extends PhotoPexels {
  index?: number;
}

type Gallery = Column[];
type Column = number[];

export { Photo, Gallery };
