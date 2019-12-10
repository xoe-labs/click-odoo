# ==============
# Custom Errors
# ==============


class ConfigError(RuntimeError):
    pass


class ConfigDirNoDirError(ConfigError):
    pass


class NoConfigDirError(ConfigError):
    pass


class ConfigDirOwnershipError(ConfigError):
    pass


class InvalidOptionError(ConfigError):
    pass


class InvalidOptionTypeError(InvalidOptionError):
    pass


class SecretError(ConfigError):
    pass


class NoSecretError(SecretError):
    pass


class SecretNoFileError(SecretError):
    pass


class SecretOwnershipError(SecretError):
    pass


class PathError(ConfigError):
    pass


class NoPathError(PathError):
    pass


class PathNoDirError(PathError):
    pass


class PathNoFileError(PathError):
    pass


class PathNotAbsoluteError(PathError):
    pass


class NoSecretsInConfigError(ConfigError):
    pass
