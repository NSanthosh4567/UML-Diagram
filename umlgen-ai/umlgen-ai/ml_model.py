
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Illustrative training data.
# Replace this with a larger, carefully labeled dataset
# before claiming production-level model accuracy.
TRAINING_TEXT = [
    "Customer extends User superclass base class",
    "Admin inherits from Account parent class",
    "PremiumUser extends User inheritance",
    "Order references Customer customer object",
    "Cart uses Product product reference",
    "Service has Repository repository field",
    "independent classes with no shared references",
    "unrelated utility functions",
    "standalone helper function",
]

TRAINING_LABELS = [
    "inheritance",
    "inheritance",
    "inheritance",
    "association",
    "association",
    "association",
    "unrelated",
    "unrelated",
    "unrelated",
]


def train_model():
    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(ngram_range=(1, 2))
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ])

    model.fit(TRAINING_TEXT, TRAINING_LABELS)
    return model


def predict_relationship(model, evidence):
    probabilities = model.predict_proba([evidence])[0]
    index = probabilities.argmax()

    return {
        "prediction": model.classes_[index],
        "confidence": float(probabilities[index])
    }
