import { paths, operations, components } from '../../openapi_schema';
import React from 'react';

interface Props {
  studio: components['schemas']['StudioPublic'];
}

function StudioCard({ studio }: Props) {
  return (
    <div className="card">
      <h3>{studio.name}</h3>
    </div>
  );
}

export { StudioCard };
