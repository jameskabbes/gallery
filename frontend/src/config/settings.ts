import { sharedConfig } from './sharedConfig';

const zIndex = {
  modalOverlay: 100,
  header: 95,
  toast: 90,
};

const validatedInput = {
  debounceTimeoutLength: 200,
};

const pagination = {
  debounceTimeoutLength: 100,
};

const scopeNameMapping: Record<string, number> =
  sharedConfig.SCOPE_NAME_MAPPING;
const scopeIdMapping: Record<string, number> = Object.entries(
  scopeNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const visibilityLevelNameMapping: Record<string, number> =
  sharedConfig.VISIBILITY_LEVEL_NAME_MAPPING;

const visibilityLevelIdMapping: Record<number, string> = Object.entries(
  visibilityLevelNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const permissionLevelNameMapping: Record<string, number> =
  sharedConfig.PERMISSION_LEVEL_NAME_MAPPING;

const permissionLevelIdMapping: Record<number, string> = Object.entries(
  permissionLevelNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const userRoleNameMapping: Record<string, number> =
  sharedConfig.USER_ROLE_NAME_MAPPING;

const userRoleIdMapping: Record<number, string> = Object.entries(
  sharedConfig.USER_ROLE_NAME_MAPPING
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

// Export the reverse mapping
export {
  zIndex,
  validatedInput,
  pagination,
  scopeIdMapping,
  visibilityLevelIdMapping,
  permissionLevelIdMapping,
  userRoleNameMapping,
  userRoleIdMapping,
};
