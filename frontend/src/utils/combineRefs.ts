import { MutableRefObject, RefCallback } from 'react';

export default function combineRefs<T>(
  ...refs: (MutableRefObject<T> | RefCallback<T> | null)[]
): RefCallback<T> {
  return (element: T) => {
    refs.forEach((ref) => {
      if (typeof ref === 'function') {
        ref(element);
      } else if (ref) {
        (ref as MutableRefObject<T | null>).current = element;
      }
    });
  };
}
