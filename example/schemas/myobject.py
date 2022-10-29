from ...api_route.models.openapi import ApiModel


class MyObject(ApiModel):
    name: str
    age: int


class MyObjectResponse(ApiModel):
    id: int
