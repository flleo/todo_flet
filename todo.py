import json
from json import JSONDecodeError
import flet as ft


def save(tasks_json=None):
    with open("tasks.json", "w") as outfile:
        json.dump(tasks_json, outfile)
        print(tasks_json)


class TodoApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.tasks_json = {}
        self.new_task_id = 0
        self.tasks = None  # self.get_tasks()
        self.new_task = None
        self.filter = None
        self.items_left = ft.Text("0 tareas pendientes")

    def build(self):
        self.new_task = ft.TextField(hint_text="Escribe una nueva tarea", autofocus=True, expand=True)
        self.tasks = ft.Column()
        self.filter = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text="Todas"),
                ft.Tab(text="Pendientes"),
                ft.Tab(text="Completadas")
            ],
        )

        # Application's root control (i.e. "view") containing all other controls
        column = ft.Column(
            width=600,
            controls=[
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked)
                    ],
                ),
                ft.Row(
                    controls=[
                        self.items_left,
                    ],
                ),
                ft.Row(
                    controls=[
                        self.filter,
                        ft.IconButton(icon=ft.icons.DELETE_OUTLINE, on_click=self.clear_clicked,  tooltip="Borra completados", )
                    ],
                ),
                ft.Column(
                    controls=[

                        self.tasks
                    ],
                ),
            ],
        )

        self.get_tasks()
        return column

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            # print(task)
            task.visible = (
                    status == "Todas"
                    or (status == "Pendientes" and task.completed is False)
                    or (status == "Completadas" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} tarea(s) pendientes"
        self.new_task.autofocus = True  # Tab pointed
        super().update()

    def get_tasks(self):
        # Opening JSON file
        with open('tasks.json', 'r') as openfile:
            # Reading from json file
            try:
                self.tasks_json = json.load(openfile)
                dic = self.tasks_json

                keys = list(dic)
                if len(keys) > 0:
                    self.new_task_id = int(keys[-1])
                    for t in keys:
                        # print(dic[t][1])
                        task = Task(dic[t][0], self.task_status_change, self.task_delete, self.tasks_json)
                        task.__dict__["_Control__uid"] = t
                        task.completed = dic[t][1]
                        self.tasks.controls.append(task)
                        # print(task.task_status_change)
                        # print(task.__dict__)
                        # self.update()
                    # print(self.tasks.controls)
                    print(f"tareas: {self.tasks_json}")
            # File is empty
            except JSONDecodeError:
                pass

    def add_clicked(self, e):
        task = Task(self.new_task.value, self.task_status_change, self.task_delete, self.tasks_json)
        self.new_task_id += 1
        ide = str(self.new_task_id)
        t = {ide: [task.task_name, task.completed]}
        task.__dict__["_Control__uid"] = ide
        self.tasks.controls.append(task)
        self.tasks_json.update(t)
        save(self.tasks_json)
        self.new_task.value = ""
        self.update()

    def task_delete(self, task):
        self.tasks_json.__delitem__(task.__dict__["_Control__uid"])
        print(self.tasks_json)
        self.tasks.controls.remove(task)
        print(task.__dict__["_Control__uid"] + ", deleted")
        save(self.tasks_json)
        self.update()

    def task_status_change(self, e):
        self.tasks_json[e.__dict__["_Control__uid"]][1] = e.completed
        # print(e.__dict__)
        # self.save()
        self.update()

    def tabs_changed(self, e):
        self.update()


class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete, tasks_json):
        super().__init__()
        self.completed = False
        self.edit_view = None
        self.display_view = None
        self.edit_name = None
        self.display_task = None
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.tasks_json = tasks_json

    def build(self):
        # self.display_task = ft.Checkbox(value=False, label=self.task_name, on_change=self.status_changed)
        self.edit_name = ft.TextField(expand=1)

        if self.completed:
            self.display_task = ft.Checkbox(
                value=True, label=self.task_name, on_change=self.status_changed
            )
        else:
            self.display_task = ft.Checkbox(
                value=False, label=self.task_name, on_change=self.status_changed
            )

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edita",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Borra",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Actualiza",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[
            self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.tasks_json[self.__dict__["_Control__uid"]][0] = self.edit_name.value
        save(self.tasks_json)
        self.update()

    def delete_clicked(self, e):
        self.task_delete(self)

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)


def main(page: ft.Page):
    page.title = "Gestor de Tareas"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 600     # Not working
    page.window_height = 500    # Not working
    page.update()

    # Create application instance
    todo = TodoApp()

    # Add application's root control to the page
    page.add(todo)


ft.app(target=main)
