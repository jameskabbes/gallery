import { paths, operations, components } from '../../openapi_schema';
import { frontendRoutes } from '../../../generateConfig';

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
