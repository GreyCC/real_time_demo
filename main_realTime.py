import datetime
import threading
import time
import tkinter as tk
import face_recognition
import numpy

from face_rec import load_players
from tkVideoPlayer import TkinterVideo
from utils import *
from tkinter.constants import RIDGE, SUNKEN


def load_widget():
    list_label = tk.Label(root, bg='Yellow', relief=RIDGE, text='Video List', font='Verdana 15')
    list_label.place(x=15, y=40, width=110)

    video_or_label = tk.Label(root, bg='#FF00FF', relief=RIDGE, text='Source Video', font='Verdana 22 bold')
    video_or_label.place(x=150 + box_w / 2 - 150, y=30, width=300, height=40)

    video_pr_label = tk.Label(root, bg='#FFFF00', relief=RIDGE, text='Processed Video', font='Verdana 22 bold')
    video_pr_label.place(x=150 + 20 + box_w / 2 * 3 - 150, y=30, width=300, height=40)


def update_duration(event):
    """ updates the duration after finding the duration """
    end_time["text"] = str(datetime.timedelta(seconds=vid_player.duration()))
    progress_slider["to"] = int(vid_player.duration() * vid_player.frame_rate())


def update_half(event):
    """ updates the scale value """
    global players_encode, players_list
    frame = vid_player.frame_img().copy()
    frame = numpy.asarray(frame)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]
    face = face_recognition.face_locations(rgb_small_frame)
    if face == []:
        sentence_text.insert(tk.END, 'No face detected\n')
    else:
        sentence_text.insert(tk.END, 'Face detected\n')
        face_encode = face_recognition.face_encodings(rgb_small_frame, face)[0]
        result = face_recognition.face_distance(players_encode, face_encode)
        if min(result) < 0.65: # Threshold
            sentence_text.insert(tk.END, 'Players name: ' + players_list[int(numpy.where(result == min(result))[0])] + '\n')
    pass


def update_frame(event):
    progress_slider.set(vid_player.current_frame()) # Update time bar
    process_frame = vid_player.frame_img().copy()

    # Add your code here


    process_frame = ImageTk.PhotoImage(process_frame)
    processed_video.config(image=process_frame)
    processed_video.image = process_frame


def comment_sentense(lan, comment):
    if lan == 'english':
        comment = comment.split()
    for i in comment:
        if lan == 'english':
            sentence_text.insert(tk.END, i + ' ')
        else:
            sentence_text.insert(tk.END, i)
        time.sleep(0.2)
    sentence_text.insert(tk.END, '\n')


def print_list():
    video_list = tk.Listbox(bg='white', relief=SUNKEN)  # Set a list
    video_list.place(x=15, y=80, width=110)  # Set position
    for i, name in enumerate(list):  # Enumerate: return [index, content]
        video_list.insert(i, name)  # List name w.r.t. index and name
    video_list.bind('<<ListboxSelect>>', load_video)  # When selected, run onselect\


def load_video(evt):
    """ loads the video """
    global players_encode, players_list
    w = evt.widget  # get widget that call this function
    index = int(w.curselection()[0])  # get the index of the object clicked
    file_path = 'Video/' + w.get(index)  # get the name accroding to the index

    # file_path = filedialog.askopenfilename()

    if file_path:
        vid_player.load(file_path)

        progress_slider.config(to=0, from_=0)
        progress_slider.set(0)

        vid_player.play()
        play_pause_btn["text"] = "Pause"
        play_pause_btn.config(bg="red")

    action_text.delete('1.0', tk.END)
    sentence_text.delete('1.0', tk.END)
    players_encode, players_list = load_players('database/' + w.get(index)[:-4])

def seek(value):
    """ used to seek a specific timeframe """
    vid_player.seekframe(int(value))


def skip(value: int):
    """ skip seconds """
    vid_player.skip_sec(value)
    progress_slider.set(progress_slider.get() + value)


def play_pause():
    """ pauses and plays """
    if vid_player.is_paused():
        vid_player.play()
        play_pause_btn["text"] = "Pause"
        play_pause_btn.config(bg="red")

    else:
        vid_player.pause()
        play_pause_btn["text"] = "Play"
        play_pause_btn.config(bg="grey")


def detect_bool():
    global obj_det
    obj_det = not obj_det
    if obj_det:
        process_btn["text"] = "Stop detection"
        process_btn.config(bg="red")
    else:
        process_btn["text"] = "Object detection"
        process_btn.config(bg="#DDDDDD")


def video_ended(event):
    """ handle video ended """
    progress_slider.set(progress_slider["to"])
    play_pause_btn["text"] = "Play"


def voice_list():
    options = ['cantonese', 'english']
    language = tk.StringVar(root)
    language.set(options[0])
    voices_list = tk.OptionMenu(root, language, *options)  # Set a list
    voices_list.place(x=150 + button_w + 60 + sentence_w, y=box_h + 150 + button_h, width=130, height=30)
    voices_list.configure(font=('Arial', 14))
    voices_list['menu'].configure(font=('Arial', 14))
    language.trace("w", lambda *args: choose_language(language.get()))


def choose_language(lan):
    global language
    try:
        voices = tts.getProperty('voices')
        for i in range(len(voices)):
            if lan == voices[i].name:
                tts.setProperty('voice', voices[i].id)
                action_text.insert(tk.END, lan + ' selected\n')
    except SyntaxError:
        action_text.insert(tk.END, lan + ' voice not installed in this computer\n')


def commentary(sentences):
    lines.append(sentences)
    comment = threading.Thread(target=start_tts, args=([lines[0]]))
    comment.start()
    lines.pop()


# SPEAK SENTENCE IN QUEUE
def start_tts(quote):
    tts.say(quote)
    tts.startLoop()


if __name__ == "__main__":
    language = 'english'
    lines = []
    players_encode, players_list = [], []
    # INIT TKINTER & UTILS:
    while True:
        root = tk.Tk()
        root.title("Tkinter media")
        root.attributes('-zoomed', True)  # Ubuntu
        # root.state('zoomed')  # Window
        # root.resizable(0, 0)  # Window
        root.update()

        root_h = root.winfo_height()
        root_w = root.winfo_width()

        box_w = (root_w - 200) / 2  # video box width
        box_h = box_w * 9 / 16  # video box height

        load_widget()
        list = call_from_folder("Video")  # Find all files in the folder
        print_list()  # List out all files

        vid_player = TkinterVideo(scaled=True, pre_load=False, master=root, bg='white', relief=SUNKEN)
        vid_player.place(x=150, y=80, width=box_w, height=box_h)

        processed_video = tk.Label(root, bg='white', relief=SUNKEN)
        processed_video.place(x=150 + 20 + box_w, y=80, width=box_w, height=box_h)

        play_pause_btn = tk.Button(root, text="Play", command=play_pause, bg="grey", font=('bold', 16))
        play_pause_btn.place(x=150, y=80 + box_h + 30, width=120, height=30)

        skip_min_5sec = tk.Button(root, text="Skip -5 sec", command=lambda: skip(-5 * 25))
        skip_min_5sec.place(x=40, y=80 + box_h + 20)

        skip_plus_5sec = tk.Button(root, text="Skip +5 sec", command=lambda: skip(5 * 25))
        skip_plus_5sec.place(x=150 + box_w, y=80 + box_h + 20)

        start_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        start_time.place(x=90, y=80 + box_h)

        end_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        end_time.place(x=150 + box_w, y=80 + box_h)

        progress_slider = tk.Scale(root, from_=0, to=0, orient="horizontal", showvalue=0, command=seek)
        progress_slider.place(x=150, y=80 + box_h, width=box_w)

        vid_player.bind("<<Duration>>", update_duration)
        vid_player.bind("<<halfSecondChanged>>", update_half)
        vid_player.bind("<<FrameChanged>>", update_frame)
        vid_player.bind("<<Ended>>", video_ended)

        obj_det = False
        process_btn = tk.Button(root, text="Object Detect", command=detect_bool, bg="#DDDDDD", font=20)
        process_btn.place(x=150 + box_w + 300, y=80 + box_h + 30, width=150)

        button_w = int(root_w * 0.2)
        button_h = root_h - box_h - 220
        action_label = tk.Label(root, text='Action', font='Verdana 12 bold')
        action_label.place(x=150, y=80 + box_h + 100)

        action_text = tk.Text(root, bg='#FDFDFD', relief=SUNKEN, font='Verdana 14')
        action_text.place(x=150, y=80 + box_h + 130, width=button_w, height=button_h)

        sentence_w = int(root_w * 0.4)
        sentence_label = tk.Label(root, text='Sentence', font='Verdana 12 bold')
        sentence_label.place(x=150 + button_w + 50, y=80 + box_h + 100)

        sentence_text = tk.Text(root, bg='#FDFDFD', relief=SUNKEN, font='Verdana 14')
        sentence_text.place(x=150 + button_w + 50, y=80 + box_h + 130, width=sentence_w, height=button_h)

        voice_list()
        tts = pyttsx3.init()
        rate = tts.getProperty('rate')
        tts.setProperty('rate', rate - 20)
        voices = tts.getProperty('voices')
        sentence_text.insert(tk.END, 'This computer have installed: ')
        for i in range(len(voices)):
            if 'english' == voices[i].name or 'cantonese' in voices[i].name:
                sentence_text.insert(tk.END, '\n' + voices[i].name)
        choose_language('cantonese')
        break

root.mainloop()
