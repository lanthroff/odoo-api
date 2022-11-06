# -*- coding: utf-8 -*-

# Copyright © Educacode.

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.models import BaseModel as OdooBaseModel

from .schema import Todo, TodoCreate, TodoListResponse, TodoPatch


class ApiProfileController(http.Controller):
    @http.route("/todo", type="api", auth="user", methods=["GET"])
    def todo_list(self, **kw) -> TodoListResponse:
        todo_ids = http.request.env["example.todo"].search(
            [("create_uid", "=", http.request.session.uid)]
        )
        return TodoListResponse(
            **{
                "todos": [
                    {
                        "id": el.id,
                        "name": el.name,
                        "content": el.content,
                        "update_date": el.write_date,
                    }
                    for el in todo_ids
                ],
            }
        )

    @http.route("/put_todo", type="api", auth="user", methods=["PUT"])
    def todo_put(self, todo: TodoCreate) -> TodoListResponse:
        http.request.env["example.todo"].create(todo.dict())

        todo_ids = http.request.env["example.todo"].search(
            [("create_uid", "=", http.request.session.uid)]
        )
        return TodoListResponse(
            todos=[
                {
                    "id": el.id,
                    "name": el.name,
                    "content": el.content,
                    "update_date": el.write_date,
                }
                for el in todo_ids
            ],
        )

    @http.route(
        "/delete_todo/<model('example.todo'):item>",
        type="api",
        auth="user",
        methods=["DELETE"],
    )
    def todo_delete(self, item):
        if item.create_uid.id == http.request.session.uid:
            item.unlink()
        return {"success": True}

    @http.route(
        "/patch_todo/<model('example.todo'):item>",
        type="api",
        auth="user",
        methods=["PATCH"],
    )
    def todo_patch(
        self, todo: TodoPatch = None, item: OdooBaseModel = None, **kw
    ) -> Todo:
        item.update(todo.dict())
        return Todo(
            id=item.id,
            name=item.name,
            content=item.content,
            update_date=item.write_date,
        )
