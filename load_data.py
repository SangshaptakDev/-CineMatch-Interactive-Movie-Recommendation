import os
import pandas as pd
import sqlite3

def main():
    # 1. Absolute paths
    csv_path = r"C:\CINEMAPHILE\indian movies.csv"
    db_dir   = r"C:\CINEMAPHILE\db"
    db_path  = os.path.join(db_dir, "movies.sqlite")

    # 2. Load CSV
    print(f"Loading data from:\n  {csv_path}")
    df = pd.read_csv(csv_path)

    # 3. Show actual columns so you can confirm names
    print("Columns found in CSV:")
    for col in df.columns:
        print("  ", repr(col))
    
    # 4. Auto‑detect title & rating columns
    title_col  = next((c for c in df.columns if "Movie" in c and "Name" in c), None)
    rating_col = next((c for c in df.columns if "Rating" in c), None)

    if not title_col or not rating_col:
        raise KeyError(
            "Could not auto‑detect your title or rating column.\n"
            f"Found columns: {df.columns.tolist()}\n"
            "Make sure one column name contains 'Movie' and 'Name', and one contains 'Rating'."
        )

    print(f"\nUsing:\n  title column = {repr(title_col)}\n  rating column = {repr(rating_col)}\n")

    # 5. Clean data
    df.drop_duplicates(inplace=True)
    df.dropna(subset=[title_col, "Genre", rating_col], inplace=True)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # 6. Ensure the db folder exists
    os.makedirs(db_dir, exist_ok=True)

    # 7. Write to SQLite
    print(f"Saving cleaned data to:\n  {db_path}")
    conn = sqlite3.connect(db_path)
    df.to_sql("movies", conn, if_exists="replace", index=False)
    conn.close()

    print("\n✅ Done! 'movies.sqlite' created in 'db/' with table 'movies'.")

if __name__ == "__main__":
    main()
