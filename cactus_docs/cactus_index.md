# Cactus Index API (Vector Database)

Source: https://docs.cactuscompute.com/latest/docs/cactus_index/

A C FFI for an on-device vector database used for RAG.

## Storage Architecture

Memory-mapped files:
- `index.bin` — embeddings (FP16) + metadata pointers
- `data.bin` — document content + metadata (UTF-8)

All embeddings are automatically normalized to unit length. Similarity is **cosine similarity**, sorted highest-first.

## Type

```c
typedef void* cactus_index_t;
```

## Functions

### cactus_index_init

```c
cactus_index_t cactus_index_init(const char* index_dir, size_t embedding_dim);
```

- `index_dir` — directory for index file storage
- `embedding_dim` — dimension of embeddings (must match for existing indexes)

Returns index handle on success, NULL on failure.

```c
cactus_index_t index = cactus_index_init("./my_index", 768);
if (!index) {
    fprintf(stderr, "Failed to initialize index\n");
    return -1;
}
```

### cactus_index_add

```c
int cactus_index_add(
    cactus_index_t index,
    const int* ids,
    const char** documents,
    const char** metadatas,
    const float** embeddings,
    size_t count,
    size_t embedding_dim
);
```

Constraints:
- IDs must be unique integers
- Max 65535 bytes per document content
- Max 65535 bytes per metadata entry
- Embedding dim must match init
- Individual document strings can be NULL (stored as empty)
- Metadata array can be NULL or individual entries can be NULL

Returns 0 on success, -1 on error.

```c
int ids[] = {1, 2};
const char* docs[] = {"AI is transforming technology", "Machine learning enables predictions"};
const char* metas[] = {"{\"source\":\"wiki\"}", "{\"source\":\"blog\"}"};

float emb1[768] = {0.1, 0.2, 0.3, /* ... */};
float emb2[768] = {0.4, 0.5, 0.6, /* ... */};
const float* embeddings[] = {emb1, emb2};

int result = cactus_index_add(index, ids, docs, metas, embeddings, 2, 768);
```

Without metadata:
```c
int result = cactus_index_add(index, ids, docs, NULL, embeddings, 2, 768);
```

### cactus_index_delete

Soft delete; space is reclaimed via `cactus_index_compact`.

```c
int cactus_index_delete(cactus_index_t index, const int* ids, size_t ids_count);
```

### cactus_index_get

Retrieves documents by IDs. Pass NULL for buffers corresponding to unused fields.

```c
int cactus_index_get(
    cactus_index_t index,
    const int* ids,
    size_t ids_count,
    char** document_buffers,
    size_t* document_buffer_sizes,
    char** metadata_buffers,
    size_t* metadata_buffer_sizes,
    float** embedding_buffers,
    size_t* embedding_buffer_sizes
);
```

Buffer-size arrays are dual-purpose:
- **Input:** capacity per buffer (bytes for docs/meta, floats for embeddings)
- **Output:** actual data written

### cactus_index_query

Cosine-similarity search.

```c
int cactus_index_query(
    cactus_index_t index,
    const float** embeddings,
    size_t embeddings_count,
    size_t embedding_dim,
    const char* options_json,
    int** id_buffers,
    size_t* id_buffer_sizes,
    float** score_buffers,
    size_t* score_buffer_sizes
);
```

Options:
```json
{
    "top_k": 10,
    "score_threshold": 0.7
}
```

Defaults: `top_k`=10, `score_threshold`=-1.0 (no filtering).

```c
float query1[768] = {/* ... */};
float query2[768] = {/* ... */};
const float* queries[] = {query1, query2};

int* ids[2];
float* scores[2];
for (int i = 0; i < 2; i++) {
    ids[i] = (int*)malloc(5 * sizeof(int));
    scores[i] = (float*)malloc(5 * sizeof(float));
}

size_t id_sizes[2] = {5, 5};
size_t score_sizes[2] = {5, 5};

int result = cactus_index_query(index, queries, 2, 768, "{\"top_k\":5}",
                                ids, id_sizes,
                                scores, score_sizes);
```

### cactus_index_compact

Removes deleted documents and reclaims disk space.

```c
int cactus_index_compact(cactus_index_t index);
```

### cactus_index_destroy

```c
void cactus_index_destroy(cactus_index_t index);
```

## Full RAG Example

```c
cactus_index_t index = cactus_index_init("./my_index", 768);
if (!index) return -1;

float query_embedding[768] = {/* ... */};
const float* queries[] = {query_embedding};

int* result_ids[1];
float* result_scores[1];
result_ids[0] = (int*)malloc(10 * sizeof(int));
result_scores[0] = (float*)malloc(10 * sizeof(float));

size_t id_sizes[1] = {10};
size_t score_sizes[1] = {10};

int query_result = cactus_index_query(index, queries, 1, 768,
                                      "{\"top_k\":3,\"score_threshold\":0.5}",
                                      result_ids, id_sizes,
                                      result_scores, score_sizes);

if (query_result == 0) {
    size_t num_results = id_sizes[0];
    char* docs[10];
    for (size_t i = 0; i < num_results; i++) docs[i] = (char*)malloc(65536);

    size_t doc_sizes[10];
    for (size_t i = 0; i < num_results; i++) doc_sizes[i] = 65536;

    int get_result = cactus_index_get(index, result_ids[0], num_results,
                                      docs, doc_sizes,
                                      NULL, NULL,
                                      NULL, NULL);

    if (get_result == 0) {
        char context[32768] = "";
        for (size_t i = 0; i < num_results; i++) {
            strcat(context, docs[i]);
            strcat(context, "\n\n");
        }
        printf("Context: %s\n", context);
    }
}

cactus_index_destroy(index);
```

## Migrate Embedding Model

```c
cactus_index_t old_index = cactus_index_init("./old_index", 768);
cactus_index_t new_index = cactus_index_init("./new_index", 1536);

int all_doc_ids[] = {1, 2, 3, 4, 5};
char* old_docs[5];
char* old_metas[5];
for (int i = 0; i < 5; i++) {
    old_docs[i] = malloc(65536);
    old_metas[i] = malloc(65536);
}
size_t doc_sizes[5] = {65536,65536,65536,65536,65536};
size_t meta_sizes[5] = {65536,65536,65536,65536,65536};

cactus_index_get(old_index, all_doc_ids, 5,
                 old_docs, doc_sizes, old_metas, meta_sizes, NULL, NULL);

float new_embs[5][1536];
const float* new_emb_ptrs[5];
for (int i = 0; i < 5; i++) {
    // recompute embeddings with the new model...
    new_emb_ptrs[i] = new_embs[i];
}

const char* doc_ptrs[5];
const char* meta_ptrs[5];
for (int i = 0; i < 5; i++) {
    doc_ptrs[i] = old_docs[i];
    meta_ptrs[i] = old_metas[i];
}

cactus_index_add(new_index, all_doc_ids, doc_ptrs, meta_ptrs,
                 new_emb_ptrs, 5, 1536);
```

## Best Practices

1. Check returns (0 = success, -1 = error). Use `cactus_get_last_error()` for details.
2. Buffer sizes: document/metadata in **bytes**, embedding in **floats**.
3. Pass NULL for unused buffers in `cactus_index_get`.
4. Always call `cactus_index_destroy()` when done.
5. One index instance per thread.
6. Batch 100–1000 documents per `cactus_index_add` call.
