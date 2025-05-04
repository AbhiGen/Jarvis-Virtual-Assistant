from Frontend.Graphics.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import firstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")  # Default to "User" if not found
AssistantName = env_vars.get("AssistantName", "Jarvis")  # Default to "Jarvis" if not found
DefaultMessage = f'''{Username}: Hello {AssistantName}, How are you?
{AssistantName}: Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNotChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:
            if len(File.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except FileNotFoundError:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatJsonLog():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def ChatLogIntegration():
    json_data = ReadChatJsonLog()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    # Ensure Username and AssistantName are strings
    formatted_chatlog = formatted_chatlog.replace("User", f"{Username} ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", f"{AssistantName} ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as File:
            Data = File.read()
        if len(str(Data)) > 0:
            lines = Data.split('\n')
            result = '\n'.join(lines)
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(result)
    except FileNotFoundError:
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNotChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

# Run initial execution
try:
    InitialExecution()
except Exception as e:
    print(f"Error in InitialExecution: {e}")
    SetAssistantStatus("Error occurred during initialization")

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    Decision = firstLayerDMM(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    G = any([True for i in Decision if i.startswith("general")])
    R = any([True for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join([ " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")])
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneratoion.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{AssistantName}: {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general", "").strip()
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime", "").strip()
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." not in AIStatus:
                SetAssistantStatus("Available...")
            sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()