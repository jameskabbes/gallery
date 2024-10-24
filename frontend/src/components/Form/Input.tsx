// import React, { useEffect, useRef } from 'react';
// import { InputState, InputValue } from '../../types';

// interface BaseInputProps<T> {
//   state: InputState<T>;
//   setState: React.Dispatch<React.SetStateAction<InputState<T>>>;
//   id: string;
//   type: string;
//   checkValidity?: boolean;
//   checkAvailability?: boolean;
//   isValid?: (value: InputState<T>['value']) => ValidityCheckReturn;
//   isAvailable?: (value: InputState<T>['value']) => Promise<boolean>;
//   required?: boolean;
//   className?: string;
//   value?: InputValue;
//   checked?: boolean;
//   children?: React.ReactNode;
//   style?: React.CSSProperties;
//   disabled?: boolean;
// }

// interface InputProps<T> extends BaseInputProps<T> {
//   onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
// }

// function Input<T>({
//   state,
//   setState,
//   id,
//   type,
//   onChange,
//   checkValidity = false,
//   checkAvailability = false,
//   isValid = (value: InputState<T>['value']) => ({ valid: true }),
//   isAvailable = async (value: InputState<T>['value']) => true,
//   required = false,
//   className = '',
//   children = null,
//   ...rest
// }: InputProps<T>) {
//   return (
//     <>
//       <input
//         className={`${className} dark:[color-scheme:dark]`}
//         type={type}
//         id={id}
//         required={required}
//         onChange={onChange}
//         {...rest}
//       />
//       {children}
//     </>
//   );
// }

// export { Input, BaseInputProps, InputProps };
