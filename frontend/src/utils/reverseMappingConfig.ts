// Import the static JSON file
import config from '../../../config.json';

// Generate the reverse mapping
const scopeIdToName = Object.entries(config.scope_name_mapping).reduce(
  (acc, [key, value]) => {
    acc[value] = key;
    return acc;
  },
  {} as { [key: number]: string }
);

const visibilityLevelIdToName = Object.entries(
  config.visibility_level_name_mapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as { [key: number]: string });

const permissionLevelIdToName = Object.entries(
  config.permission_level_name_mapping
).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as { [key: number]: string });

//
const userRoleIdToName = Object.entries(config.user_role_name_mapping).reduce(
  (acc, [key, value]) => {
    acc[value] = key;
    return acc;
  },
  {} as { [key: number]: string }
);

// Export the reverse mapping
export {
  scopeIdToName,
  visibilityLevelIdToName,
  permissionLevelIdToName,
  userRoleIdToName,
};
