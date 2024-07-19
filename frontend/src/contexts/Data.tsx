import React, { useReducer, createContext } from 'react';
import { components } from '../openapi_schema';
import { DataContext as DataContextType } from '../types';

import {
  studiosReducer,
  studiosReducerDefaultState,
} from '../components/Studio/studiosReducer';

const DataContext = createContext<DataContextType>({
  studios: null,
});

interface Props {
  children: React.ReactNode;
}

function DataContextProvider({ children }: Props) {
  const [studiosState, studiosDispatch] = useReducer(
    studiosReducer,
    studiosReducerDefaultState
  );

  return (
    <DataContext.Provider
      value={{
        studios: { state: studiosState, dispatch: studiosDispatch },
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export { DataContext, DataContextProvider };
