import configJson from './config.json';
import { Config } from './config';

const config: Config = configJson as Config;

export { config };
