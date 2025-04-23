import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import joblib
import os

# 1. Load your data
engine = create_engine("sqlite:///movies.sqlite")  # Path is local to this script
df = pd.read_sql("SELECT * FROM movies", engine)

# 2. Recreate your text_features & vectorizer
df["text_features"] = (df["Genre"].fillna("") + " " + df["Movie Name"].fillna(""))
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(df["text_features"])

# 3. Build your indices mapping
indices = pd.Series(df.index, index=df["Movie Name"]).drop_duplicates()

# 4. Save them in db/ directory (same as script location)
joblib.dump(tfidf, "tfidf_vectorizer.joblib")
sparse.save_npz("tfidf_matrix.npz", tfidf_matrix)
joblib.dump(indices, "indices.joblib")

print("✅ Artifacts saved in db/: vectorizer, matrix (sparse), indices.")
