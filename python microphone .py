import speech_recognition as sr
import pyttsx3
import requests
import datetime
import time
import re

# ------------------ Initialize Engine ------------------
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

def speak(text):
    """Convert text to speech"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to user using microphone"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... 🎙")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}\n")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
            return ""
        except Exception:
            speak("Something went wrong while listening.")
            return ""

# ------------------ Features ------------------

def get_weather(city="Mumbai"):
    """Fetch weather from OpenWeatherMap API"""
    api_key = "your_api_key"  
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") == 200:
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        speak(f"The current temperature in {city} is {temp}°C with {desc}")
    else:
        speak(f"Sorry, I couldn't fetch the weather for {city} right now.")

def get_news():
    """Fetch latest news using NewsAPI key"""
    api_key = "your_api_key"
    url = f"https://newsapi.org/v2/everything?q=India&sortBy=publishedAt&language=en&apiKey={api_key}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:5]
    if articles:
        speak("Here are the latest news updates:")
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            speak(f"Headline {i}: {title}")
    else:
        speak("Sorry, I couldn't fetch the news right now.")

reminders = []

def set_reminder(task, delay):
    remind_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    reminders.append((task, remind_time))
    speak(f"Reminder set for {task} in {delay} seconds.")

def check_reminders():
    now = datetime.datetime.now()
    for reminder in reminders[:]:
        task, remind_time = reminder
        if now >= remind_time:
            speak(f"Reminder: {task}")
            reminders.remove(reminder)

# ------------------ Command Processing ------------------

def assistant():
    speak("Hello, I am your personal assistant. How can I help you today?")
    while True:
        command = listen()
        if not command:
            continue

        # --- Weather ---
        if "weather" in command:
            # Try to extract city from command
            match = re.search(r'weather in (\w+)', command)
            if match:
                city = match.group(1)
            else:
                speak("Which city?")
                city = listen()
            if city:
                get_weather(city)

        # --- News ---
        elif "news" in command:
            get_news()

        # --- Reminder ---
        elif "reminder" in command or "remind me" in command:
            speak("What should I remind you about?")
            task = listen()
            speak("In how many seconds?")
            try:
                seconds = int(listen())
                set_reminder(task, seconds)
            except ValueError:
                speak("Sorry, I need a number in seconds.")

        # --- Time ---
        elif "time" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {now}")

        # --- Exit ---
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

        check_reminders()

# ------------------ Run ------------------

if __name__ == "__main__":
    assistant()