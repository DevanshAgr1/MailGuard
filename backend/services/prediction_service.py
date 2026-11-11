import re, string, time
from pathlib import Path
import pickle

BASE = Path(__file__).resolve().parents[2]
MODELS = BASE / 'models'

class PredictionService:
    def __init__(self):
        with open(MODELS / 'spam_model.pkl', 'rb') as f:
            self.model = pickle.load(f)
        with open(MODELS / 'tfidf_vectorizer.pkl', 'rb') as f:
            self.tfidf = pickle.load(f)

    @staticmethod
    def clean_text(text):
        text = str(text or '')
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+|bit\.ly\S+', ' URLTOKEN ', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', ' NUMTOKEN ', text)
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def signals(text):
        raw = str(text or '')
        low = raw.lower()
        signals = []
        if re.search(r'https?://|www\.|bit\.ly', low): signals.append('External URL detected')
        if re.search(r'\b(urgent|immediately|act now|limited time|winner|congratulations|claim|free|prize|offer)\b', low): signals.append('Urgency or promotional language')
        if re.search(r'[$€£₹]\s?\d|\b\d+[,.]?\d*\s?(usd|inr|dollars|rupees)\b', low): signals.append('Currency / financial indicator')
        if raw.count('!') >= 2: signals.append('High exclamation usage')
        if len(re.findall(r'[A-Z]', raw)) > max(8, len(raw) * .25): signals.append('Unusual capitalization')
        if re.search(r'\b(password|otp|verify|account|login|bank|payment)\b', low): signals.append('Account or verification language')
        if len(raw.split()) > 70: signals.append('Long message structure')
        return signals[:5] or ['No strong heuristic signals detected']

    def predict(self, text):
        if not str(text or '').strip():
            raise ValueError('Message cannot be empty.')
        start = time.perf_counter()
        cleaned = self.clean_text(text)
        vec = self.tfidf.transform([cleaned])
        pred = int(self.model.predict(vec)[0])
        if hasattr(self.model, 'predict_proba'):
            confidence = float(max(self.model.predict_proba(vec)[0]))
        else:
            score = float(self.model.decision_function(vec)[0])
            confidence = 1 / (1 + __import__('math').exp(-abs(score)))
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        stats = {
            'characters': len(text),
            'words': len(str(text).split()),
            'urls': len(re.findall(r'https?://|www\.|bit\.ly', str(text), re.I)),
            'numbers': len(re.findall(r'\d+', str(text))),
            'exclamations': str(text).count('!'),
            'uppercase_ratio': round(sum(c.isupper() for c in str(text)) / max(1, sum(c.isalpha() for c in str(text))), 3)
        }
        risk = 'high' if pred and confidence >= .85 else 'medium' if pred else 'low'
        return {
            'prediction': 'spam' if pred else 'ham',
            'label': 'SPAM' if pred else 'NOT SPAM',
            'confidence': round(confidence, 4),
            'confidence_percent': round(confidence * 100, 2),
            'risk_level': risk,
            'signals': self.signals(text),
            'statistics': stats,
            'processing_time_ms': elapsed,
        }
