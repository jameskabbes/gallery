import { paths, operations, components } from '../../openapi_schema';
import siteConfig from '../../../siteConfig.json';

function getGalleryLink(
  galleryId: components['schemas']['Gallery']['id']
): string {
  return `${siteConfig.galleriesUrlBase}/${galleryId}`;
}

export { getGalleryLink };
