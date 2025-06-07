"use client";

import { TodoCommand } from "@/commands/todo";
import { sendNotification } from "@tauri-apps/plugin-notification";
import dayjs from "dayjs";
import { useEffect, useState } from "react";

export default function TodoCard() {
  const [task, setTask] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [nowTime, setNowTime] = useState(dayjs());

  // タスク一覧はオブジェクトで管理
  const [todos, setTodos] = useState<{ text: string; due: string }[]>([]);

  useEffect(() => {
    TodoCommand.loadTodos().then((data) => setTodos(data));
  }, []);
  useEffect(() => {
    todos.forEach((todo) => {
    const isToday = dayjs().isSame(dayjs(todo.due), "day");
    if (isToday) {
      sendNotification({
        title: "今日のタスク",
        body: `「${todo.text}」の期限は今日です。`,
      });
    }
  });
      TodoCommand.saveTodos(todos);
  }, [todos]);
  const checkDueTodos = (todos: { text: string; due: string }[]) => {
  const today = dayjs().format("YYYY-MM-DD");
  todos.forEach((todo) => {
    if (todo.due === today) {
      sendNotification({
        title: "本日のタスク通知",
        body: `タスク「${todo.text}」の期限は本日です。`,
      });
    }
  });
};
  const handleAdd = () => {
    if (!task.trim() || !dueDate) return;
    setTodos([...todos, { text: task.trim(), due: dueDate }]);
    setTask("");
    setDueDate("");
  };
  const handleDelete = (index: number) => {
    setTodos(todos.filter((_, i) => i !== index));
  };

  return (
    <div className="max-w-xl mx-auto mt-20 p-8 bg-white rounded-2xl shadow-xl border border-gray-200">
      <h1 className="text-3xl font-bold mb-2 text-center text-gray-800">
        My Todo App
      </h1>
      <p className="text-center text-gray-500 mb-6">
        今日やることを整理しましょう
      </p>

      <div className="flex flex-col gap-4 mb-6">
        <input
          type="text"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="タスクを入力..."
          className="px-4 py-2 border rounded-lg text-black"
        />

        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="px-4 py-2 border rounded-lg text-black"
        />

        <button
          onClick={handleAdd}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
        >
          追加
        </button>
      </div>

      <ul className="space-y-2">
        {todos.map((todo, index) => (
          <li
            key={index}
            className="p-4 bg-blue-50 border rounded-lg flex justify-between items-center"
          >
            <div>
              <p className="font-medium text-gray-800">{todo.text}</p>
              <p className="text-sm text-gray-500">期限: {todo.due}</p>
            </div>
            <button
              onClick={() => handleDelete(index)}
              className="text-red-500 hover:text-red-700"
              aria-label="削除"
            >
              削除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
