import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import os from 'os';
import { warn } from 'console';

function userConfigDir(appName: string): string {
  const home = os.homedir();
  const platform = os.platform();

  if (platform === 'win32') {
    const appData = process.env.APPDATA || path.join(home, 'AppData', 'Local');
    return path.join(appData, appName);
  } else if (platform === 'darwin') {
    return path.join(home, 'Library', 'Application Support', appName);
  } else {
    return path.join(home, '.config', appName);
  }
}

function convertEnvPathToAbsolute(rootDir: string, a: string): string {
  if (path.isAbsolute(a)) {
    return a;
  } else {
    return path.resolve(rootDir, a);
  }
}

const configDir = userConfigDir('arbor_imago');

const _appEnv = process.env.APP_ENV || null;
const _configEnvDir = process.env.CONFIG_ENV_DIR || null;

let configEnvDir: string | null = null;

if (_configEnvDir != null) {
  const configEnvDir = convertEnvPathToAbsolute(configDir, _configEnvDir);
} else if (_appEnv != null) {
  const configEnvDir = path.join(configDir, _appEnv);
} else {
  const configEnvDir = path.join(configDir, 'dev');
  warn(
    'Neither APP_ENV nor configEnvDir is set. Defaulting to dev environment.'
  );
}

const sharedConfigEnvDir = path.join(configEnvDir, 'shared');
const sharedConfigEnvYamlPath = path.join(sharedConfigEnvDir, 'config.yaml');

if (!fs.existsSync(sharedConfigEnvYamlPath)) {
  throw new Error(
    `sharedConfigEnvYamlPath does not exist: ${sharedConfigEnvYamlPath}`
  );
}

export interface SharedConfigEnv {
  BACKEND_URL: string;
  FRONTEND_URL: string;
  AUTH_KEY: string;
  HEADER_KEYS: Record<string, string>;
  FRONTEND_ROUTES: Record<string, string>;
  SCOPE_NAME_MAPPING: Record<string, number>;
  VISIBILITY_LEVEL_NAME_MAPPING: Record<string, number>;
  PERMISSION_LEVEL_NAME_MAPPING: Record<string, number>;
  USER_ROLE_NAME_MAPPING: Record<string, number>;
  USER_ROLE_SCOPES: Record<string, string[]>;
  OPENAPI_SCHEMA_PATH: string;
  OTP_LENGTH: number;
  GOOGLE_CLIENT_ID: string;
}

function loadSharedConfig(): SharedConfigEnv {
  const file = fs.readFileSync(sharedConfigEnvYamlPath, 'utf8');
  return yaml.load(file) as SharedConfigEnv;
}

export const sharedConfig = loadSharedConfig();
