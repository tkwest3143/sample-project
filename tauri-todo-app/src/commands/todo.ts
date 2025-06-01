import { invoke } from "@tauri-apps/api/core";

type Todo = { text: string; due: string };
export class TodoCommand {
  static async saveTodos(todos: Todo[]) {
    await invoke("save_todos", { todos });
  }
  static async loadTodos(): Promise<Todo[]> {
    return await invoke("load_todos");
  }
}
    