import { execFileSync } from 'child_process';
import { config } from './src/config/config';
import os from 'os';
import path from 'path';

const relativeOpenapiSchemaPath = path.relative(
  process.cwd(),
  config.openapiSchemaPath
);

const cliSchemaPath = relativeOpenapiSchemaPath.split(path.sep).join('/');

const outputPath = './src/openapi_schema.d.ts';
const command = 'npx';
const args = ['openapi-typescript', cliSchemaPath, '-o', outputPath];

try {
  execFileSync(command, args, {
    stdio: 'inherit',
    shell: os.platform() === 'win32', // Use shell on Windows
  });
} catch (err) {
  console.error('Failed to generate openapi types:', err);
  process.exit(1);
}
