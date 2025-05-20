import React, {
  useState,
  useReducer,
  useCallback,
  createContext,
  useEffect,
  useMemo,
  useRef,
} from 'react';
import { ModalsContextType, ModalType } from '../types';

export const ModalsContext = createContext<ModalsContextType>({
  activeModal: null,
  pushModals: () => {},
  updateModals: () => {},
  upsertModals: () => {},
  deleteModals: () => {},
  swapActiveModal: () => {},
});

export function ModalsContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [modals, setModals] = useState<Record<ModalType['key'], ModalType>>({});
  const [keys, setKeys] = useState<ModalType['key'][]>([]);
  const [activeModal, setActiveModal] = useState<ModalType | null>(null);

  const modalsRef = useRef(modals);
  const keysRef = useRef(keys);
  const activeModalVersion = useRef<number>(0);

  useEffect(() => {
    modalsRef.current = modals;
  }, [modals]);

  useEffect(() => {
    keysRef.current = keys;
  }, [keys]);

  useEffect(() => {
    setActiveModal(
      keysRef.current.length > 0
        ? modalsRef.current[keysRef.current[keysRef.current.length - 1]]
        : null
    );
  }, [activeModalVersion.current]);

  const pushModals: ModalsContextType['pushModals'] = useCallback((modals) => {
    setModals((prevModals) => {
      for (const modal of modals) {
        if (prevModals[modal.key]) {
          throw new Error(`Push: Modal with key ${modal.key} already exists`);
        }
      }
      const newModals = { ...prevModals };
      for (const modal of modals) {
        newModals[modal.key] = modal;
      }
      return newModals;
    });
    setKeys((prevKeys) => {
      const newKeys = [...prevKeys];
      for (const modal of modals) {
        newKeys.push(modal.key);
      }
      return newKeys;
    });
    activeModalVersion.current += 1;
  }, []);

  const updateModals: ModalsContextType['updateModals'] = useCallback(
    (modals) => {
      setModals((prevModals) => {
        const newModals = { ...prevModals };
        for (const modal of modals) {
          if (!prevModals[modal.key]) {
            throw new Error(
              `Update: Modal with key ${modal.key} does not exist`
            );
          }
          newModals[modal.key] = {
            ...prevModals[modal.key],
            ...modal,
            // merge componentProps
            componentProps: {
              ...prevModals[modal.key].componentProps,
              ...modal.componentProps,
            },
          };
          if (keysRef.current[keysRef.current.length - 1] === modal.key) {
            activeModalVersion.current += 1;
          }
        }
        return newModals;
      });
    },
    []
  );

  const upsertModals: ModalsContextType['upsertModals'] = useCallback(
    (modals) => {
      setModals((prevModals) => {
        const newModals = { ...prevModals };
        for (const modal of modals) {
          newModals[modal.key] = modal;
        }
        return newModals;
      });

      setKeys((prevKeys) => {
        const newKeys = [...prevKeys];
        let isNewActiveVersion = false;
        for (const modal of modals) {
          if (!prevKeys.includes(modal.key)) {
            newKeys.push(modal.key);
          }
          if (newKeys[newKeys.length - 1] === modal.key) {
            isNewActiveVersion = true;
          }
        }
        if (isNewActiveVersion) {
          activeModalVersion.current += 1;
        }
        return newKeys;
      });
    },
    []
  );

  const deleteModals: ModalsContextType['deleteModals'] = useCallback(
    (keys) => {
      setModals((prevModals) => {
        setKeys((prevModalKeys) => {
          const newModalKeys = [...prevModalKeys];
          const originalLastKey = newModalKeys[newModalKeys.length - 1];

          for (const key of keys) {
            if (!prevModals[key]) {
              throw new Error(`Delete: Modal with key ${key} does not exist`);
            }
            const modalKeyIndex = prevModalKeys.indexOf(key);
            if (modalKeyIndex === -1) {
              throw new Error(
                `Delete: Modal with key ${key} not found in keys`
              );
            }
            newModalKeys.splice(modalKeyIndex, 1);
          }

          if (newModalKeys[newModalKeys.length - 1] !== originalLastKey) {
            activeModalVersion.current += 1;
          }
          return newModalKeys;
        });

        const newModals = { ...prevModals };
        for (const key of keys) {
          delete newModals[key];
        }
        return newModals;
      });
    },
    []
  );

  const swapActiveModal: ModalsContextType['swapActiveModal'] = useCallback(
    (modal) => {
      setActiveModal((prevActiveModal) => {
        setModals((prevModals) => {
          const newModals = { ...prevModals };
          if (prevActiveModal) {
            delete newModals[prevActiveModal.key];
          }
          newModals[modal.key] = modal;
          return newModals;
        });
        setKeys((prevModalKeys) => {
          const newModalKeys = [...prevModalKeys];
          if (prevActiveModal) {
            newModalKeys.pop();
          }
          newModalKeys.push(modal.key);
          return newModalKeys;
        });
        activeModalVersion.current += 1;

        return modal;
      });
    },
    []
  );

  return (
    <ModalsContext.Provider
      value={{
        activeModal,
        pushModals,
        updateModals,
        upsertModals,
        deleteModals,
        swapActiveModal,
      }}
    >
      {children}
    </ModalsContext.Provider>
  );
}
