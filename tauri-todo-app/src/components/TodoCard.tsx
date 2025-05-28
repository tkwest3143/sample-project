"use client";

import { useState } from "react";

export default function TodoCard() {
  const [task, setTask] = useState("");
  const [todos, setTodos] = useState<string[]>([]);

  const handleAdd = () => {
    if (!task.trim()) return;
    setTodos([...todos, task.trim()]);
    setTask("");
  };

  return (
    <div className="max-w-xl mx-auto mt-20 p-8 bg-white rounded-2xl shadow-xl border border-gray-200">
      <h1 className="text-3xl font-bold mb-2 text-center text-gray-800">
        My Todo App
      </h1>
      <p className="text-center text-gray-500 mb-6">
        今日やることを整理しましょう
      </p>

      <div className="flex items-center gap-2 mb-6">
        <input
          type="text"
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
          placeholder="タスクを入力..."
          value={task}
          onChange={(e) => setTask(e.target.value)}
        />
        <button
          onClick={handleAdd}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg transition duration-150"
        >
          追加
        </button>
      </div>

      <ul className="space-y-2">
        {todos.map((todo, index) => (
          <li
            key={index}
            className="px-4 py-3 bg-blue-50 border border-blue-100 rounded-lg text-gray-800 shadow-sm"
          >
            {todo}
          </li>
        ))}
      </ul>
    </div>
  );
}
