import React from 'react';

function Toast(): JSX.Element {
  return (
    <div className="fixed bottom-0 right-0 p-4 m-4 bg-gray-800 text-white rounded-lg">
      <p>Toast</p>
    </div>
  );
}

export { Toast };
