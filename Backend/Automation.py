# Import required libraries
from AppOpener import open as appopen, close  # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import load_dotenv, dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard-related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.

# ✅ Load environment variables from the .env file.
load_dotenv(".env")
env_vars = dotenv_values(".env")  # ✅ Correct usage after importing
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.

# Define CSS classes for parsing specific elements in HTML content.
classes = ["_1cubwf", "hgKElc", "LTKOO sYyrIc", "ZRLCw", "gsrt vk_bk fZVnSb YwPint", "pcLqee", "TW-Data-text tw-text-small tw-ta", "_1zgcRDc", "OSuObd LTKOO", "VLyY6g", "webanswers-webanswers_table webanswers-table", "dDoNo ibxkbb gsrt", "SKlaOe", "LmkFke", "VQfAg", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36"

# Initializes the Groq client with the API Key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = {"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letter"}

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)
    return True


# Function to generate content using AI and save it to a file.
def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[SystemChatBot] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    file_path = f"Data\\{Topic.lower().replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        pass

    def extract_links(html):
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', {'jsname': 'UmckNb'})
        return [link.get('href') for link in links]

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": useragent}
        response = sess.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to retrieve search results.")
            return None

    html = search_google(app)
    if html:
        link = extract_links(html)[0]
        webopen(link)
    return True

def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
CloseApp("settngs")
def System(command):
    def mute():
        keyboard.press_and_release("volume mute")
    def unmute():
        keyboard.press_and_release("volume mute")
    def volume_up():
        keyboard.press_and_release("volume up")
    def volume_down():
        keyboard.press_and_release("volume down")
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file " in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"[red]Unknown command: {command}[/red]")
    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            if result:
                yield result
            else:
                yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    # Example usage of the Automation function.
    commands = ["open chrome", "google search Python programming", "play Python tutorial"]
    asyncio.run(Automation(commands))