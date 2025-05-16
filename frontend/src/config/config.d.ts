interface Config {
  backendUrl: string;
  frontendUrl: string;
  authKey: string;
  headerKeys: Record<string, string>;
  frontendRoutes: Record<string, string>;
  scopeNameMapping: Record<string, number>;
  scopeIdMapping: Record<number, string>;
  visibilityLevelNameMapping: Record<string, number>;
  visibilityLevelIdMapping: Record<number, string>;
  permissionLevelNameMapping: Record<string, number>;
  permissionLevelIdMapping: Record<number, string>;
  userRoleNameMapping: Record<string, number>;
  userRoleIdMapping: Record<number, string>;
  userRoleScopes: Record<string, string[]>;
  otpLength: number;
  googleClientId: string;
  vite: {
    server: {
      port: number;
      host: boolean;
    };
  };
  openapiSchemaPath: string;
}

export { Config };
