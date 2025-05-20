import { paths, operations, components } from '../../openapi_schema';
import { config } from '../../config/config';

export function getGalleryLink(
  galleryId: components['schemas']['GalleryPublic']['id'] | null
): string {
  if (!galleryId) {
    return config.frontendRoutes.galleries;
  } else {
    return `${config.frontendRoutes.galleries}/${galleryId}`;
  }
}
