import React from 'react';
import { IoClose } from 'react-icons/io5';
import { IoCheckmark } from 'react-icons/io5';

function CheckOrX({ value }: { value: boolean }) {
  return value ? (
    <IoCheckmark className="text-green-500" />
  ) : (
    <IoClose className="text-red-500" />
  );
}

export { CheckOrX };
