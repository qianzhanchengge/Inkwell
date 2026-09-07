// 个人工作台 MongoDB 初始化脚本（§4.2）
// 创建集合与索引

db = db.getSiblingDB("workbench");

// 笔记内容集合
db.createCollection("note_contents");
db.note_contents.createIndex({ note_id: 1 });
db.note_contents.createIndex({ user_id: 1 });
db.note_contents.createIndex({ content: "text" });

// 文章内容集合
db.createCollection("article_contents");
db.article_contents.createIndex({ article_id: 1 });
db.article_contents.createIndex({ user_id: 1 });
db.article_contents.createIndex({ content: "text" });
