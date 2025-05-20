type Action =
  | { type: 'SET_VALUE'; value: number }
  | { type: 'SET_NULL' }
  | { type: 'INCREMENT'; nPhotos: number }
  | { type: 'DECREMENT'; nPhotos: number };

type v = number | null;

export function reducer(value: v, action: Action): v {
  switch (action.type) {
    case 'SET_VALUE':
      return action.value;

    case 'SET_NULL':
      return null;

    case 'INCREMENT':
      if (value !== null) {
        let ind = (value + 1) % action.nPhotos;
        return ind;
      }
      return value;

    case 'DECREMENT':
      if (value !== null) {
        value = value - 1;
        while (value < 0) {
          value += action.nPhotos;
        }
        return value;
      }
      return value;

    default:
      return value;
  }
}
