import React from 'react';
import { IoClose } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';
import { InputStatus } from '../../types';
import { Loader2 } from '../Utils/Loader';

function CheckOrX({ status }: { status: InputStatus }) {
  switch (status) {
    case 'valid':
      return <IoCheckmark className="text-green-500" />;
    case 'invalid':
      return <IoClose className="text-red-500" />;
    case 'loading':
      return <Loader2 />;
  }
}

export { CheckOrX };
