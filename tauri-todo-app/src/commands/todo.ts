import { invoke } from "@tauri-apps/api/core";
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
  Visibility,
} from '@tauri-apps/plugin-notification';

type Todo = { text: string; due: string };
export class TodoCommand {
  static async saveTodos(todos: Todo[]) {
    await invoke("save_todos", { todos });
  }
  static async loadTodos(): Promise<Todo[]> {
    return await invoke("load_todos");
  }
}
    