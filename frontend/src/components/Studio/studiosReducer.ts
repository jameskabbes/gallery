import { components } from '../../openapi_schema';
import { StudiosReducerState, StudiosReducerAction } from '../../types';

const studiosReducerDefaultState: StudiosReducerState = new Map();

function studiosReducer(
  state: StudiosReducerState,
  action: StudiosReducerAction
): StudiosReducerState {
  switch (action.type) {
    case 'SET':
      return action.payload;
    case 'ADD':
      const newState = new Map(state);
      newState.set(action.payload.id, action.payload);
      return newState;
    case 'DELETE':
      console.log(action.payload);
      const newStateDelete = new Map(state);
      newStateDelete.delete(action.payload);
      return newStateDelete;
    default:
      return state;
  }
}

export { studiosReducer, studiosReducerDefaultState };
