import json
import pickle
import re
import string
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                              precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

DATA = Path("data/spam_data.csv")
MODELS = Path("models"); MODELS.mkdir(exist_ok=True)
ASSETS = Path("assets"); ASSETS.mkdir(exist_ok=True)

# 1. Load
df = pd.read_csv(DATA)
print("Shape:", df.shape)
print(df["label"].value_counts())

# 2. Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|bit\.ly\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["clean_message"] = df["message"].apply(clean_text)
df["msg_length"] = df["message"].apply(len)
df["word_count"] = df["message"].apply(lambda x: len(x.split()))

# 3. EDA plot: class distribution + message length
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.countplot(x="label", data=df, ax=axes[0], palette="Set2")
axes[0].set_title("Class Distribution (Spam vs Ham)")
sns.histplot(data=df, x="msg_length", hue="label", kde=True, ax=axes[1], bins=30)
axes[1].set_title("Message Length Distribution")
plt.tight_layout()
plt.savefig(ASSETS / "eda_overview.png", dpi=110)
plt.close()

# 4. Encode target
df["target"] = df["label"].map({"ham": 0, "spam": 1})

X = df["clean_message"]
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. TF-IDF vectorization
tfidf = TfidfVectorizer(max_features=3000, stop_words="english", ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# 6. Train & compare models
candidates = {
    "Multinomial Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Linear SVM": LinearSVC(),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
}

results = []
best_name, best_score, best_model = None, -1, None
preds_store = {}

for name, clf in candidates.items():
    clf.fit(X_train_tfidf, y_train)
    pred = clf.predict(X_test_tfidf)
    preds_store[name] = pred
    acc = accuracy_score(y_test, pred)
    prec = precision_score(y_test, pred)
    rec = recall_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    try:
        proba = clf.predict_proba(X_test_tfidf)[:, 1]
        auc = roc_auc_score(y_test, proba)
    except AttributeError:
        auc = roc_auc_score(y_test, clf.decision_function(X_test_tfidf))
    results.append({"model": name, "accuracy": acc, "precision": prec,
                     "recall": rec, "f1": f1, "roc_auc": auc})
    if f1 > best_score:
        best_name, best_score, best_model = name, f1, clf

results_df = pd.DataFrame(results).sort_values("f1", ascending=False)
results_df.to_csv(MODELS / "model_comparison.csv", index=False)
print(results_df)

# 7. Confusion matrix for the best model
cm = confusion_matrix(y_test, preds_store[best_name])
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Ham", "Spam"], yticklabels=["Ham", "Spam"])
plt.title(f"Confusion Matrix — {best_name}")
plt.xlabel("Predicted"); plt.ylabel("Actual")
plt.tight_layout()
plt.savefig(ASSETS / "confusion_matrix.png", dpi=110)
plt.close()

# 8. Save artifacts
with open(MODELS / "spam_model.pkl", "wb") as f:
    pickle.dump(best_model, f)
with open(MODELS / "tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)

metadata = {
    "best_model": best_name,
    "metrics": results_df.iloc[0].to_dict(),
    "n_samples": int(len(df)),
    "n_features": int(X_train_tfidf.shape[1]),
}
(MODELS / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str))

print("\nBest model:", best_name)
print("Saved artifacts to models/ and assets/")
