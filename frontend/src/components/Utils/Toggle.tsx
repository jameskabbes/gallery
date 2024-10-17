import React from 'react';

interface ToggleProps {
  state: boolean;
  handleToggle: () => void;
}

function Toggle({ state, handleToggle }: ToggleProps) {
  return (
    <div
      onClick={handleToggle}
      className="rounded-full p-1 component-bg-color border-2"
      style={{ height: '2rem', width: '4rem', position: 'relative' }}
    >
      <div
        className="rounded-full bg-primary h-full aspect-square transition-transform duration-100"
        style={{ transform: state ? 'translateX(2rem)' : 'translateX(0)' }}
      ></div>
    </div>
  );
}

export { Toggle };
