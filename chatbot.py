
import random
import re
from datetime import datetime
from difflib import get_close_matches

BOT_NAME = "CodeBot"


INTENTS = {
    "greeting": {
        "patterns": ["hello", "hi", "hey", "hii", "namaste", "good morning",
                     "good afternoon", "good evening"],
        "responses": ["Hi!", "Hello! 👋", "Hey there!", "Namaste! 🙏"],
    },
    "how_are_you": {
        "patterns": ["how are you", "how r u", "kaise ho", "kya haal hai", "how are you doing"],
        "responses": ["I'm fine, thanks!", "Doing great, thanks for asking! How about you?",
                      "Main badhiya hoon! Aap kaise ho?"],
    },
    "feeling_good": {
        "patterns": ["i am fine", "i'm fine", "i am good", "i'm good", "main theek hoon", "badhiya"],
        "responses": ["Glad to hear that! 😊", "That's great!"],
    },
    "feeling_bad": {
        "patterns": ["i am sad", "i'm sad", "not good", "i am tired", "i'm tired", "bored"],
        "responses": ["Sorry to hear that. Take a short break, it helps!",
                      "Hang in there! Want to hear a joke?"],
    },
    "name_bot": {
        "patterns": ["what is your name", "who are you", "your name", "tumhara naam kya hai"],
        "responses": [f"I'm {BOT_NAME}, a rule-based chatbot built with Python."],
    },
    "creator": {
        "patterns": ["who made you", "who created you", "who built you", "your creator"],
        "responses": ["I was built by Prageshwar Kumar as part of the CodeAlpha Python internship."],
    },
    "capabilities": {
        "patterns": ["what can you do", "help me", "your features", "what do you do"],
        "responses": ["I can chat, tell time/date, jokes, do simple maths (try: calculate 12 * 5), "
                      "and remember your name. Type 'help' for all commands."],
    },
    "thanks": {
        "patterns": ["thanks", "thank you", "thx", "shukriya", "dhanyavad"],
        "responses": ["You're welcome!", "Anytime! 😊", "Happy to help!"],
    },
    "python": {
        "patterns": ["what is python", "tell me about python", "python kya hai"],
        "responses": ["Python is a high-level, beginner-friendly programming language used in "
                      "web dev, automation, data science and AI."],
    },
    "bye": {
        "patterns": ["bye", "goodbye", "see you", "exit", "quit", "alvida", "tata"],
        "responses": ["Goodbye!", "See you soon! 👋", "Bye! Take care."],
    },
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "There are 10 types of people: those who understand binary and those who don't.",
    "A SQL query walks into a bar, sees two tables and asks: 'Can I join you?'",
    "Why did the Python programmer wear glasses? Because he couldn't C! 😄",
]

FALLBACKS = [
    "Sorry, I didn't understand that. Can you rephrase?",
    "Hmm, I'm still learning. Try 'help' to see what I can do.",
    "I don't know that one yet. Ask me something else!",
]


PHRASE_TO_INTENT = {p: name for name, data in INTENTS.items() for p in data["patterns"]}



def clean(text: str) -> str:
    """Lowercase, remove punctuation and extra spaces."""
    text = re.sub(r"[^\w\s']", " ", text.lower())
    return " ".join(text.split())


def match_intent(user_text: str):
    """Return intent name or None. Tries: exact -> word-boundary -> fuzzy."""
    if user_text in PHRASE_TO_INTENT:
        return PHRASE_TO_INTENT[user_text]


    for phrase in sorted(PHRASE_TO_INTENT, key=len, reverse=True):
        if re.search(rf"\b{re.escape(phrase)}\b", user_text):
            return PHRASE_TO_INTENT[phrase]


    close = get_close_matches(user_text, PHRASE_TO_INTENT.keys(), n=1, cutoff=0.8)
    return PHRASE_TO_INTENT[close[0]] if close else None


def safe_calculate(expression: str) -> str:
    """Evaluate simple maths safely (only digits and + - * / ( ) . %)."""
    if not re.fullmatch(r"[\d\s+\-*/().%]+", expression):
        return "I can only calculate numbers with + - * / ( ) operators."
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # safe: characters are whitelisted
        return f"The answer is {round(result, 4)}"
    except ZeroDivisionError:
        return "You can't divide by zero!"
    except Exception:
        return "That doesn't look like a valid calculation."



class ChatBot:
    def __init__(self):
        self.user_name = None
        self.history = []          

    def special_commands(self, raw: str, text: str):
        """Handle commands that need logic instead of fixed replies."""
       
        m = re.search(r"(?:my name is|i am called|mera naam|call me)\s+([a-zA-Z]+)", text)
        if m:
            self.user_name = m.group(1).capitalize()
            return f"Nice to meet you, {self.user_name}! 😊"

        if re.search(r"\b(what('s| is) my name|mera naam kya hai)\b", text):
            return (f"Your name is {self.user_name}." if self.user_name
                    else "You haven't told me your name yet. Say 'my name is ...'")

        if re.search(r"\b(time|samay)\b", text) and "date" not in text:
            return f"The time is {datetime.now():%I:%M %p}."

        if re.search(r"\b(date|today|aaj)\b", text):
            return f"Today is {datetime.now():%A, %d %B %Y}."

        if re.search(r"\bjoke\b", text):
            return random.choice(JOKES)

        calc = re.match(r"(?:calculate|calc|solve)\s+(.+)", raw.lower())
        if calc:
            return safe_calculate(calc.group(1))

        if text == "help":
            return ("Commands: hello | how are you | what is your name | time | date | joke | "
                    "calculate 5 * 8 | my name is <name> | what is python | save | bye")
        return None

    def reply(self, raw: str) -> str:
        text = clean(raw)
        if not text:
            return "Please type something."

        answer = self.special_commands(raw, text)
        if answer is None:
            intent = match_intent(text)
            answer = random.choice(INTENTS[intent]["responses"]) if intent else random.choice(FALLBACKS)
            if intent == "greeting" and self.user_name:
                answer = re.sub(r"[^\w]+$", "", answer) + f", {self.user_name}!"

        self.history.append(("You", raw))
        self.history.append((BOT_NAME, answer))
        return answer

    def is_goodbye(self, raw: str) -> bool:
        return match_intent(clean(raw)) == "bye"

    def save_chat(self, filename="chat_history.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Chat saved on {datetime.now():%Y-%m-%d %H:%M:%S}\n" + "-" * 40 + "\n")
            for speaker, msg in self.history:
                f.write(f"{speaker}: {msg}\n")
        return filename


def main():
    bot = ChatBot()
    print(f"{BOT_NAME}: Hi! I'm {BOT_NAME}. Type 'help' for commands, 'bye' to exit.")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{BOT_NAME}: Goodbye!")
            break

        if clean(user_input) == "save":
            print(f"{BOT_NAME}: Chat saved to {bot.save_chat()}")
            continue

        response = bot.reply(user_input)
        print(f"{BOT_NAME}: {response}")

        if bot.is_goodbye(user_input):
            bot.save_chat()
            break


if __name__ == "__main__":
    main()