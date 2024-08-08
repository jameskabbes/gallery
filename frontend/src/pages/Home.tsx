import React, { useEffect } from 'react';

function Home() {
  return (
    <div>
      <h1>Home</h1>
      <div className="flex flex-col space-y-2 w-fit">
        <button className="button-base">Base</button>
        <button className="button-primary">Primary</button>
        <button className="button-secondary">Secondary</button>
        <button className="button-valid">Valid</button>
        <button className="button-invalid">Invalid</button>
        <button>Button</button>
      </div>
    </div>
  );
}

export { Home };
