import React from 'react';
import { IoClose } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';
import { InputStatus } from '../../types';
import { Surface } from '../Utils/Surface';

function CheckOrX({ status }: { status: InputStatus }) {
  switch (status) {
    case 'valid':
      return <IoCheckmark className="text-green-500" />;
    case 'invalid':
      return <IoClose className="text-red-500" />;
    case 'loading':
      return <Surface className="loader1 mb-0"></Surface>;
  }
}

export { CheckOrX };
