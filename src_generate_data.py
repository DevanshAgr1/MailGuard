"""
Generates a synthetic SMS/Email spam-vs-ham dataset in the classic
'SMS Spam Collection' style, since no external dataset download is
available in this environment. Mirrors realistic spam/ham phrasing.
"""
import random
import pandas as pd
from pathlib import Path

random.seed(42)

spam_templates = [
    "Congratulations! You have WON a {prize} prize. Claim now by calling {phone}",
    "URGENT: Your account has been suspended. Verify immediately at {link}",
    "FREE entry into our {prize} draw. Text WIN to {phone} now!",
    "You have been selected for a FREE {prize}. Click {link} to claim before it expires",
    "Limited time offer! Get {prize} absolutely FREE. Reply YES to {phone}",
    "Your loan of Rs.{amount} has been approved. Confirm at {link}",
    "WINNER!! As a valued customer you have won a {prize}. Call {phone} to claim",
    "Get rich quick! Invest {amount} today and double it in 7 days. Visit {link}",
    "Your {bank} account needs verification. Update details at {link} to avoid suspension",
    "Cash prize of Rs.{amount} waiting for you! Claim now at {link}",
    "Hot singles in your area want to chat! Click {link} now",
    "Final notice: pay Rs.{amount} now or your service will be disconnected. Pay at {link}",
    "Free recharge of Rs.{amount} is waiting. Click {link} to redeem instantly",
    "Dear customer, your {bank} card is blocked. Call {phone} immediately to unblock",
    "Earn Rs.{amount} per day working from home! No experience needed. Join at {link}",
]

ham_templates = [
    "Hey, are we still meeting for {activity} tomorrow?",
    "Can you send me the notes from {subject} class?",
    "Don't forget to submit the {subject} assignment by {day}",
    "I'll be reaching home by {time}, start dinner without me",
    "Thanks for helping me with the {subject} project yesterday",
    "Let's catch up for {activity} this weekend, are you free?",
    "The {subject} exam has been postponed to next {day}",
    "Can you pick up milk on your way back home?",
    "Meeting with the team is scheduled at {time} today",
    "Happy birthday! Hope you have a wonderful day",
    "I reached the office, will call you after the {activity}",
    "Please review the {subject} report I sent and share feedback",
    "Mom said dinner will be ready by {time}, come home soon",
    "Are you coming for {activity} practice today evening?",
    "Just checking in, how did your {subject} interview go?",
]

prizes = ["cash", "iPhone", "holiday package", "laptop", "gift voucher", "smartwatch", "lottery"]
phones = ["9876543210", "8001234567", "7009988776", "9123456780"]
links = ["bit.ly/claim-now", "secure-verify.co", "win-prizes.net", "quick-cash.in"]
amounts = ["5000", "10000", "25000", "50000", "1,00,000"]
banks = ["SBI", "HDFC", "ICICI", "Axis"]
activities = ["lunch", "movie", "cricket", "study group", "coffee"]
subjects = ["Maths", "Physics", "AIML", "Chemistry", "English"]
days = ["Monday", "Friday", "Tuesday", "Thursday"]
times = ["7 pm", "8:30 pm", "6 pm", "9 pm"]

spam_extra = ["", " Act now!", " Don't miss out!", " Offer valid today only.", " T&C apply.", " Hurry, limited slots!"]
ham_extra = ["", " Let me know.", " Thanks!", " See you then.", " Take care.", " :)"]
ham_prefix = ["", "Hi, ", "Hey, ", "Hello, ", "Hi there, "]

def fill(template, extra_pool, prefix_pool=None):
    text = template.format(
        prize=random.choice(prizes), phone=random.choice(phones),
        link=random.choice(links), amount=random.choice(amounts),
        bank=random.choice(banks), activity=random.choice(activities),
        subject=random.choice(subjects), day=random.choice(days),
        time=random.choice(times),
    )
    prefix = random.choice(prefix_pool) if prefix_pool else ""
    return prefix + text + random.choice(extra_pool)

n_per_class = 500
rows = []
seen = set()
attempts = 0
while len([r for r in rows if r["label"] == "spam"]) < n_per_class and attempts < 20000:
    attempts += 1
    msg = fill(random.choice(spam_templates), spam_extra)
    if msg not in seen:
        seen.add(msg)
        rows.append({"label": "spam", "message": msg})

attempts = 0
while len([r for r in rows if r["label"] == "ham"]) < n_per_class and attempts < 20000:
    attempts += 1
    msg = fill(random.choice(ham_templates), ham_extra, ham_prefix)
    if msg not in seen:
        seen.add(msg)
        rows.append({"label": "ham", "message": msg})

# Add some overlapping / ambiguous examples so the classes aren't
# trivially separable (mirrors real-world noisy spam/ham data)
tricky_ham = [
    "Congratulations on your promotion! Let's celebrate this weekend",
    "You have won the office quiz contest, collect your prize from HR",
    "Reminder: your gym membership renewal is due, call the front desk",
    "Your Amazon order has been delivered, thanks for shopping with us",
    "Free pizza for the team today to celebrate the project launch!",
    "Your account statement for this month is ready, check the email",
    "Offer for you: 20% off at the campus canteen this week only",
    "Please verify your seat number before the exam starts tomorrow",
]
tricky_spam = [
    "Hi, it's your bank calling about a pending transaction, call back urgently",
    "Hey buddy, I saw an amazing investment deal, want details? Reply now",
    "Team, HR wants you to update your salary account link immediately",
    "Reminder: complete your KYC today or your SIM will be deactivated",
]
for t in tricky_ham:
    rows.append({"label": "ham", "message": t})
for t in tricky_spam:
    rows.append({"label": "spam", "message": t})

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
df = df.drop_duplicates(subset="message").reset_index(drop=True)

out = Path("data/spam_data.csv")
out.parent.mkdir(exist_ok=True)
df.to_csv(out, index=False)
print(f"Saved {len(df)} rows to {out}")
print(df['label'].value_counts())
