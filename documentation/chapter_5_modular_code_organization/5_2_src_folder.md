### 5.2 “src/” Folder

Contains the actual pipeline steps (one script per data transformation version). Each script typically:
1. Reads config values (paths, columns, etc.).
2. Reads in data from a CSV or DB.
3. Applies the transformation logic.
4. Saves the new data version + logs metadata.
