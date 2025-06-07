#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![save_todos, load_todos])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
struct Todo {
    text: String,
    due: String,
}
#[tauri::command]
fn save_todos(todos: Vec<Todo>) -> Result<(), String> {
    let dir = get_data_directory();
    let path = dir.join("todos.json");
    let json = serde_json::to_string_pretty(&todos).map_err(|e| e.to_string())?;
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    File::create(&path)
        .and_then(|mut f| f.write_all(json.as_bytes()))
        .map_err(|e| e.to_string())?;
    Ok(())
}
#[tauri::command]
fn load_todos() -> Result<Vec<Todo>, String> {
    let dir = get_data_directory();
    let path = dir.join("todos.json");
    if !path.exists() {
        return Ok(Vec::new());
    }
    let mut file = File::open(&path).map_err(|e| e.to_string())?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)
        .map_err(|e| e.to_string())?;
    serde_json::from_str(&contents).map_err(|e| e.to_string())
}

// データベースのパスを取得する関数
fn get_data_directory() -> PathBuf {
    PathBuf::from(if cfg!(debug_assertions) {
        "target/debug/data"
    } else {
        "data"
    })
}
