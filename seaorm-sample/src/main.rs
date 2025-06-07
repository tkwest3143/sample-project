use sea_orm::{Database, DatabaseConnection, EntityTrait};

pub mod entities;
fn main() {
    async_std::task::block_on(async {
        if let Err(e) = db_connection().await {
            eprintln!("DB error: {:?}", e);
        }
    });
}
async fn db_connection() -> Result<(), sea_orm::DbErr> {
    let db: DatabaseConnection = Database::connect("sqlite://db.sqlite?mode=rwc").await?;
    // 新しい投稿データを作成（titleとtextをセット、他のフィールドはデフォルト値）
    let data = entities::post::ActiveModel {
    title: sea_orm::ActiveValue::Set("Sample Title".to_owned()),
    text: sea_orm::ActiveValue::Set("Sample text content".to_owned()),
      ..Default::default()
    };
    // データベースに投稿を挿入
    entities::post::Entity::insert(data).exec(&db).await?;
    // 投稿テーブルから1件だけ取得
    let cheese: Option<entities::post::Model> = entities::post::Entity::find().one(&db).await?;
    if let Some(post) = cheese {
        println!("Post found: {:?}", post);
    } else {
        println!("No post found.");
    }
    Ok(())
}
