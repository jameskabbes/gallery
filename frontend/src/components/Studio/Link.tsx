import React from 'react';
import { paths, operations, components } from '../../openapi_schema';

type Props = {
  studio_id: components['schemas']['StudioID'];
  children: React.ReactNode;
};

function Link({ studio_id, children }: Props) {
  return <a href={`/studios/${studio_id}`}>{children}</a>;
}

export { Link };
