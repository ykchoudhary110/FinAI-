-- FTS5 Full Text Search Tables for FinAI (0002_add_fts5.sql)

CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
    source_type, -- 'chat', 'expense', 'report', 'knowledge'
    source_id,
    title,
    content
);
