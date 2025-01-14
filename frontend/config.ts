// Import the static JSON file
import config from '../config.json';
import constants from '../constants.json';

const zIndex = {
  modalOverlay: 100,
  header: 95,
  toast: 90,
};

const validatedInput = {
  debounceTimeoutLength: 200,
};

const scopeNameMapping: Record<string, number> = constants.scope_name_mapping;
const scopeIdMapping: Record<string, number> = Object.entries(
  scopeNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const visibilityLevelNameMapping: Record<string, number> =
  constants.visibility_level_name_mapping;

const visibilityLevelIdMapping: Record<number, string> = Object.entries(
  visibilityLevelNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const permissionLevelNameMapping: Record<string, number> =
  constants.permission_level_name_mapping;

const permissionLevelIdMapping: Record<number, string> = Object.entries(
  permissionLevelNameMapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

const userRoleNameMapping: Record<string, number> =
  constants.user_role_name_mapping;

const userRoleIdMapping: Record<number, string> = Object.entries(
  constants.user_role_name_mapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as {});

// Export the reverse mapping
export {
  zIndex,
  validatedInput,
  scopeIdMapping,
  visibilityLevelIdMapping,
  permissionLevelIdMapping,
  userRoleIdMapping,
};
