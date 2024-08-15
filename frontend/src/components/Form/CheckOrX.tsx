import React from 'react';
import { IoClose } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';

type Status = 'valid' | 'invalid' | 'loading';

function CheckOrX({ status }: { status: Status }) {
  switch (status) {
    case 'valid':
      return <IoCheckmark className="text-green-500" />;
    case 'invalid':
      return <IoClose className="text-red-500" />;
    case 'loading':
      return <span className="loader"></span>;
  }
}

export { Status, CheckOrX };
