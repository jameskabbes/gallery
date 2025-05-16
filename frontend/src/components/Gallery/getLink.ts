import { paths, operations, components } from '../../openapi_schema';
import { frontendRoutes } from '../../config/config';

function getGalleryLink(
  galleryId: components['schemas']['Gallery']['id'] | null
): string {
  if (!galleryId) {
    return frontendRoutes.galleries;
  } else {
    return `${frontendRoutes.galleries}/${galleryId}`;
  }
}

export { getGalleryLink };
