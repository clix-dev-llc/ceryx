import typesystem


def boolean_to_redis(value: bool):
    return "1" if value else "0"


def redis_to_boolean(value):
    return True if "1" else False


def ensure_string(value):
    redis_value = (
        None if value is None
        else value.decode("utf-8") if type(value) == bytes else str(value)
    )
    return redis_value


def value_to_redis(field, value):
    if isinstance(field, typesystem.Boolean):
        return boolean_to_redis(value)
    
    if isinstance(field, typesystem.Reference):
        return field.target.validate(value).to_redis()

    return ensure_string(value)


def redis_to_value(field, redis_value):
    if isinstance(field, typesystem.Boolean):
        return redis_to_boolean(redis_value)
    
    if isinstance(field, typesystem.Reference):
        return field.target.from_redis(redis_value)

    return ensure_string(redis_value)


class BaseSchema(typesystem.Schema):
    @classmethod
    def from_redis(cls, redis_data):
        return {
            ensure_string(key): redis_to_value(self.fields[key], value)
            for key, value in self.items()
        }

    def to_redis(self):
        return {
            ensure_string(key): value_to_redis(self.fields[key], value)
            for key, value in self.items()
        }


class Settings(BaseSchema):
    enforce_https = typesystem.Boolean(default=False)
    mode = typesystem.Choice(
        choices=(
            ("proxy", "Proxy"),
            ("redirect", "Redirect"),
        ),
        default="proxy",
    )
    certificate_path = typesystem.String(allow_null=True)
    key_path = typesystem.String(allow_null=True)


class Route(BaseSchema):
    DEFAULT_SETTINGS = dict(Settings.validate({}))

    source = typesystem.String()
    target = typesystem.String()
    settings = typesystem.Reference(Settings, default=DEFAULT_SETTINGS)
