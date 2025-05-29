class Category:
    def __init__(self, name: str) -> None:
        self.name: str = name


class Task:
    def __init__(
        self,
        text: str,
        category: str | None = None,
        custom_fields: dict[str, object] | None = None,
        completed: bool = False,
    ) -> None:
        self.text: str = text
        self.category: str | None = category
        self.custom_fields: dict[str, object] = custom_fields or {}
        self.completed: bool = completed
