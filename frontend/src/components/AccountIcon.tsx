import React from 'react';
import { IoPersonCircleOutline } from 'react-icons/io5';
import { IoMenuSharp } from 'react-icons/io5';

function AccountIcon() {
  return (
    <div className="flex flex-row rounded-full border-2 p-2">
      <IoMenuSharp />
      <IoPersonCircleOutline />
    </div>
  );
}

export { AccountIcon };
