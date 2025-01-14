import { paths, operations, components } from '../../openapi_schema';
import constants from '../../../../constants.json';

function getGalleryLink(
  galleryId: components['schemas']['Gallery']['id'] | null
): string {
  if (!galleryId) {
    return constants.frontend_urls.galleries;
  } else {
    return `${constants.frontend_urls.galleries}/${galleryId}`;
  }
}

export { getGalleryLink };
