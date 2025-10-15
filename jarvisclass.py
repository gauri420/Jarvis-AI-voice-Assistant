import pyttsx3
import speech_recognition as sr
import webbrowser
import musiclib
import requests
from openai import OpenAI
from googleapiclient.discovery import build
from datetime import datetime

class JarvisBackend:
    def __init__(self, youtube_api_key, openai_api_key, news_api_key):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.news_api_key = news_api_key
        self.client = OpenAI(api_key=openai_api_key)
        self.youtube = build("youtube", "v3", developerKey=youtube_api_key)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def aiprocess(self, command):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "you are a virtual assistant named jarvis skilled in general tasks like alexa and google cloud, give short responses please"},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message.content

    def search_youtube(self, query, max_results=1):
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            results = []
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                video_title = item["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                results.append((video_title, video_url))
            return results
        except Exception as e:
            print(f"Error: {e}")
            return []

    def process_command(self, command):
        command = command.lower()

        if "open google" in command:
            webbrowser.open("https://google.com")
        elif "hello" in command:
            self.speak("Hello How can I assist you?")
        elif "time" in command:
            self.speak(f"The current time is {datetime.now().strftime('%I:%M %p')}")
        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
        elif "open instagram" in command:
            webbrowser.open("https://instagram.com")
        elif "open facebook" in command:
            webbrowser.open("https://facebook.com")
        elif "open whatsapp" in command:
            webbrowser.open("https://whatsapp.com")
        elif command.startswith("play"):
            song = command.split(" ")[1]
            if song in musiclib.music:
                webbrowser.open(musiclib.music[song])
            else:
                self.speak(f"Sorry, I don't have {song} in my library.")
        elif "news" in command:
            self.fetch_news()
        elif "exit" in command or "stop" in command:
            self.speak("Goodbye!")
            print("Exiting JARVIS...")
            exit()
        elif "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            results = self.search_youtube(query)
            if results:
                self.speak("Here are the top results:")
                for i, (title, _) in enumerate(results, start=1):
                    print(f"{i}. {title}")
                self.speak(f"Playing {results[0][0]}")
                print(f"Opening: {results[0][1]}")
                webbrowser.open(results[0][1])
            else:
                self.speak("Sorry, I couldn't find any videos for your search.")
        else:
            output = self.aiprocess(command)
            self.speak(output)

    def fetch_news(self):
        try:
            response = requests.get(f"https://newsapi.org/v2/top-headlines?apikey={self.news_api_key}&language=en")
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                if articles:
                    self.speak("Here are the top news headlines")
                    for i, article in enumerate(articles[:5], start=1):
                        title = article["title"]
                        description = article.get("description", "No description available")
                        print(f"{i}. {title} - {description}")
                        self.speak(title)
                else:
                    self.speak("Sorry, I couldn't find any news.")
            else:
                self.speak("There was an issue retrieving the news.")
        except Exception:
            self.speak("Sorry, I couldn't fetch the news.")

    def listen_loop(self):
        while True:
            try:
                self.speak("Initializing Jarvis....")
                with sr.Microphone() as source:
                    print("Listening.......")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    print("Recognizing...")
                    trigger = self.recognizer.recognize_google(audio)

                if trigger.lower() == "jarvis":
                    self.speak("Yes?")
                    with sr.Microphone() as source:
                        print("Jarvis Active....")
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                        command = self.recognizer.recognize_google(audio)
                        self.process_command(command)

            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            except sr.RequestError:
                print("Sorry, the service is down.")



if __name__ == "__main__":
    jarvis = JarvisBackend(
        youtube_api_key="youtube_api",
        openai_api_key="Your_open_api",
        news_api_key="news_api"
    )
    jarvis.listen_loop()
