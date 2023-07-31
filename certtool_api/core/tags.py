from attrs import define, field


@define
class Tags:
    _tag_map: dict[str, str] = field(factory=dict)

    def __init__(self, **kwargs) -> None:
        self._tag_map = kwargs

    def __repr__(self) -> str:
        return self._tag_map.__repr__()

    def __bool__(self) -> bool:
        return bool(self._tag_map)

    def add_tag(self, tag_key: str, tag_value: str) -> None:
        self._tag_map.update({tag_key: tag_value})

    def add_tags(self, other: "Tags") -> None:
        self._tag_map.update(other._tag_map)

    def list(self) -> list[dict[str, str]]:
        return [
            {
                "Key": _key,
                "Value": _val,
            }
            for _key, _val in self._tag_map.items()
        ]
