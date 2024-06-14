from beanie import PydanticObjectId

# todo: switch to pydantic-extra-types.ObjectIdField once PR is merged
# todo: PR: https://github.com/pydantic/pydantic-extra-types/pull/151
# todo: should we contribute?

type ObjectID = PydanticObjectId
