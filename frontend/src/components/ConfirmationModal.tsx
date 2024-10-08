import React, { useContext, useRef } from 'react';

// interface Props {
//   title: string;
//   message: string;
//   onConfirm: () => void;
//   onCancel: () => void;
//   confirmText?: string;
//   cancelText?: string;
// }

// function ConfirmationModal({
//   title,
//   message,
//   onConfirm,
//   onCancel,
//   confirmText = 'Confirm',
//   cancelText = 'Cancel',
// }: Props): JSX.Element {
//   let modalContext = useContext(ModalsContext);

//   return (
//     <div className="p-4 card">
//       <h4>{title}</h4>
//       <p>{message}</p>
//       <div className="flex flex-row justify-center space-x-2">
//         <button
//           className="button-secondary"
//           onClick={() => {
//             onCancel();
//             modalContext.dispatch({ type: 'POP' });
//           }}
//         >
//           {cancelText}
//         </button>
//         <button
//           className="button-primary"
//           onClick={() => {
//             onConfirm();
//             modalContext.dispatch({ type: 'POP' });
//           }}
//         >
//           {confirmText}
//         </button>
//       </div>
//     </div>
//   );
// }

// export { ConfirmationModal };
