CREATE TABLE documents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_name NVARCHAR(255) NOT NULL,
    source_type NVARCHAR(50) NOT NULL,
    source_path NVARCHAR(500) NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    status NVARCHAR(50) NOT NULL DEFAULT 'processed'
);

CREATE TABLE document_chunks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id INT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text NVARCHAR(MAX) NOT NULL,
    page_number INT NULL,
    section_title NVARCHAR(255) NULL,
    vector_id NVARCHAR(255) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_document_chunks_documents
        FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE TABLE query_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    question NVARCHAR(MAX) NOT NULL,
    answer NVARCHAR(MAX) NULL,
    retrieved_chunks NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE processing_runs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id INT NOT NULL,
    run_status NVARCHAR(50) NOT NULL,
    error_message NVARCHAR(MAX) NULL,
    started_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    finished_at DATETIME2 NULL,
    CONSTRAINT FK_processing_runs_documents
        FOREIGN KEY (document_id) REFERENCES documents(id)
);