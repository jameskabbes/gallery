import React, { useEffect } from 'react';

function Home() {
  return (
    <div>
      <h1>h1</h1>
      <h2>h2</h2>
      <h3>h3</h3>
      <h4>h4</h4>
      <h5>h5</h5>
      <h6>h6</h6>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-primary-lighter h-64"></div>
        <div className="bg-primary h-64"></div>
        <div className="bg-primary-darker h-64"></div>
        <div className="bg-secondary-lighter h-64"></div>
        <div className="bg-secondary h-64"></div>
        <div className="bg-secondary-darker h-64"></div>
        <div className="bg-accent-lighter h-64"></div>
        <div className="bg-accent h-64"></div>
        <div className="bg-accent-darker h-64"></div>
        <div className="bg-light-lighter h-64"></div>
        <div className="bg-light h-64"></div>
        <div className="bg-light-darker h-64"></div>
        <div className="bg-dark-lighter h-64"></div>
        <div className="bg-dark h-64"></div>
        <div className="bg-dark-darker h-64"></div>
      </div>
    </div>
  );
}

export { Home };
