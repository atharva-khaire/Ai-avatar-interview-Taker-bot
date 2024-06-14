from flask import Flask, render_template, request
import re
import time
import os
import json
import google.generativeai as genai
from IPython.display import Markdown
from gtts import gTTS
import speech_recognition as sr
import pygame
import time
import cv2



user_responses = []

# Set your API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyBAtGOtAIGni2RBnhIBTrn71HJPU5vb7TU"

# Configure generative AI
genai.configure(api_key="AIzaSyBAtGOtAIGni2RBnhIBTrn71HJPU5vb7TU")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('interface.html')


@app.route('/choice')
def choice():
    return render_template('choice.html')

@app.route('/interView')
def interView():
    return render_template('interview.html')


@app.route('/One2One')
def One2One():
    return render_template('One2One.html')


@app.route('/generate_interview', methods=['POST'])
def generate_interview():
    query = request.form['query']
    num_questions = int(request.form['num_questions'])

        
    query = f'{query} can you generate  {num_questions} questions on the above paragraph'
    # Choose a model (replace 'gemini-pro' with your desired model)
    model_name = 'gemini-pro'
    model = genai.GenerativeModel(model_name)

    # Generate content
    response = model.generate_content(query)

    # Extract and display the generated response
    generated_text = response.text
    print(f"Generated Response:\n{generated_text}")

    str_data = f'{generated_text}'

    # Split the string into individual questions using regular expressions
    questions = re.split(r'\d+\.\s*', str_data)
    # Remove empty strings from the list
    questions = [q.strip() for q in questions if q.strip()]

    # Create an array to store each question substring
    questionArray = [question for question in questions]

    # Display the extracted questions
    for i, question in enumerate(questionArray):
        print(f"Question {i + 1}: {question}")



    def text_to_speech(questionArray , language='en'):
        for i , text in enumerate(questionArray):
            saveAs = f'output{i}.mp3'
            tts = gTTS(text = text , lang = language , slow=False)
            tts.save(saveAs)
            print("saved")




    # def speech_to_text_from_microphone():
    #     global user_responses  # Access the global array

    #     recognizer = sr.Recognizer()

    #     with sr.Microphone() as source:
    #         print("Say answer:")
    #         recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
    #         audio_data = recognizer.listen(source)

    #         try:
    #             text = recognizer.recognize_google(audio_data)
    #             print("Your answer:", text)

    #             # Store the recognized text in the global array
    #             user_responses.append(text)
    #         except sr.UnknownValueError:
    #             print("Could not understand audio")
    #         except sr.RequestError as e:
    #             print(f"Could not request results from Google Speech Recognition service; {e}")




    # def play_audio(file_path):
    #     pygame.init()
    #     pygame.mixer.init()

    #     try:
    #         pygame.mixer.music.load(file_path)
    #         pygame.mixer.music.play()

    #         while pygame.mixer.music.get_busy():
    #             # Wait for the audio to finish playing
    #             pygame.time.Clock().tick(10)

    #     except Exception as e:
    #         print(f"Error: {e}")
    #     finally:
    #         pygame.mixer.quit()

    text_to_speech(questionArray)

    return render_template('One2One.html')

@app.route('/Quize')
def Quize():
    return render_template('Quize.html')


@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    query = request.form['query']
    num_questions = int(request.form['num_questions'])

    # Generate questions
    query = f'{query} Can you generate {num_questions} questions on the above paragraph question should be in MCQ type. Quiz format should be like this: **Question ----------- (a) option a (b) option b (c) option c (d) option d'
    model_name = 'gemini-pro'
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(query)
    generated_text = response.text

    # Extract questions and options
    lines = generated_text.strip().split('\n')
    questions = []
    options_a = []
    options_b = []
    options_c = []
    options_d = []

    current_question = ""
    current_a = ""
    current_b = ""
    current_c = ""
    current_d = ""

    for line in lines:
        line = line.strip()
        if line.startswith("**Question"):
            if current_question:
                questions.append(current_question.strip())
                options_a.append(current_a.strip())
                options_b.append(current_b.strip())
                options_c.append(current_c.strip())
                options_d.append(current_d.strip())
            current_question = ""
            current_a = ""
            current_b = ""
            current_c = ""
            current_d = ""
        elif line.startswith("(a)"):
            current_a = line.replace("(a)", "").strip()
        elif line.startswith("(b)"):
            current_b = line.replace("(b)", "").strip()
        elif line.startswith("(c)"):
            current_c = line.replace("(c)", "").strip()
        elif line.startswith("(d)"):
            current_d = line.replace("(d)", "").strip()
        else:
            if current_question:
                current_question += " " + line.strip()
            else:
                current_question = line.strip()

    if current_question:
        questions.append(current_question.strip())
        options_a.append(current_a.strip())
        options_b.append(current_b.strip())
        options_c.append(current_c.strip())
        options_d.append(current_d.strip())

    # Convert lists to JSON
    questions_json = json.dumps(questions)
    options_a_json = json.dumps(options_a)
    options_b_json = json.dumps(options_b)
    options_c_json = json.dumps(options_c)
    options_d_json = json.dumps(options_d)

    return render_template('CreateQuiz.html', questions=questions_json, options_a=options_a_json, options_b=options_b_json, options_c=options_c_json, options_d=options_d_json)


@app.route('/startInterview')
def startInterview():
    for i in range(0 , 3):
        audio_file_path = f'output{i}.mp3'
        play_videos(i)
        play_audio(audio_file_path)
        speech_to_text_from_microphone()
    

def play_videos(start_index=0):
    while True:
        file_name = f"result_voice ({start_index}).mp4"  # Assuming video files are in .mp4 format
        if not os.path.exists(file_name):
            print(f"No more video files found starting from index {start_index}.")
            break

        cap = cv2.VideoCapture(file_name)
        
        if not cap.isOpened():
            print(f"Error opening video file: {file_name}")
            break

        print(f"Playing video file: {file_name}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print(f"Finished playing video file: {file_name}")
                break
            cv2.imshow('Video Playback', frame)
            
            if cv2.waitKey(25) & 0xFF == ord('q'):
                print("Playback interrupted by user.")
                cap.release()
                cv2.destroyAllWindows()
                return
        
        cap.release()
        start_index += 1

    cv2.destroyAllWindows()


def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            # Wait for the audio to finish playing
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.mixer.quit()



def speech_to_text_from_microphone():
    global user_responses  # Access the global array

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio_data = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio_data)
            print("You said:", text)

            # Store the recognized text in the global array
            user_responses.append(text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

def text_to_speech(questionArray , language='en'):
    for i , text in enumerate(questionArray):
        saveAs = f'output{i}.mp3'
        tts = gTTS(text = text , lang = language , slow=False)
        tts.save(saveAs)
        print("saved")

if __name__ == '__main__':
    app.run(debug=True)
