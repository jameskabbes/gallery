import { paths, operations, components } from '../../openapi_schema';
import siteConfig from '../../../siteConfig.json';

function getGalleryLink(gallery: components['schemas']['Gallery']): string {
  return `${siteConfig.galleriesUrlBase}/${gallery.id}`;
}

export { getGalleryLink };
