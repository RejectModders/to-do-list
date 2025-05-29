from app.models import Category, Task


class ToDoController:
    def __init__(self) -> None:
        self.categories: list[Category] = [
            Category("All"),
            Category("Work"),
            Category("Personal"),
            Category("Shopping"),
        ]
        self.tasks: list[Task] = []

    def add_category(self, name: str) -> bool:
        if name and name not in [c.name for c in self.categories]:
            self.categories.append(Category(name))
            return True
        return False

    def add_task(
        self, title: str, category: str | None, **custom_fields: object
    ) -> Task:
        task = Task(title, category=category, custom_fields=custom_fields)
        self.tasks.append(task)
        return task

    def edit_task(
        self,
        index: int,
        category: str | None,
        title: str,
        **custom_fields: object,
    ) -> bool:
        filtered: list[Task] = self.get_tasks_by_category(category)
        if 0 <= index < len(filtered):
            task = filtered[index]
            task.text = title
            task.custom_fields = custom_fields
            return True
        return False

    def complete_task(self, index: int, category: str | None) -> bool:
        filtered: list[Task] = self.get_tasks_by_category(category)
        if 0 <= index < len(filtered):
            task = filtered[index]
            task.completed = True
            return True
        return False

    def delete_task(self, index: int, category: str | None) -> bool:
        filtered: list[Task] = self.get_tasks_by_category(category)
        if 0 <= index < len(filtered):
            task = filtered[index]
            self.tasks.remove(task)
            return True
        return False

    def get_tasks_by_category(self, category: str | None) -> list[Task]:
        if category == "All":
            return self.tasks
        return [
            t for t in self.tasks if getattr(t, "category", None) == category
        ]

    def delete_category(self, name: str) -> bool:
        if name == "All":
            return False
        self.categories = [c for c in self.categories if c.name != name]
        self.tasks = [
            t for t in self.tasks if getattr(t, "category", None) != name
        ]
        return True
