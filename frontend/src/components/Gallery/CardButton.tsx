import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CardButton } from '../Utils/Card';
import { paths, operations, components } from '../../openapi_schema';
import { getGalleryLink } from './getLink';

interface Props {
  gallery: components['schemas']['GalleryPublic'];
}

export function GalleryCardButton({ gallery }: Props) {
  const navigate = useNavigate();

  return (
    <CardButton
      onClick={() => {
        navigate(getGalleryLink(gallery.id));
      }}
    >
      <h2>{gallery.name}</h2>
      <p>{gallery.description}</p>
    </CardButton>
  );
}
