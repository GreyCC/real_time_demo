import datetime
import threading
import time
import tkinter as tk
import cv2
import pyttsx3
import numpy

from tkVideoPlayer import TkinterVideo
from utils import *
from tkinter.constants import RIDGE, SUNKEN
from pytorchyolo import detect, models
from augmentation import *
from multiprocessing.pool import ThreadPool as Pool


def load_widget():
    list_label = tk.Label(root, bg='Yellow', relief=RIDGE, text='Video List', font='Verdana 15')
    list_label.place(x=15, y=40, width=110)

    video_or_label = tk.Label(root, bg='#FF00FF', relief=RIDGE, text='Source Video', font='Verdana 22 bold')
    video_or_label.place(x=150 + box_w / 2 - 150, y=30, width=300, height=40)

    video_pr_label = tk.Label(root, bg='#FFFF00', relief=RIDGE, text='Processed Video', font='Verdana 22 bold')
    video_pr_label.place(x=150 + 20 + box_w / 2 * 3 - 150, y=30, width=300, height=40)

    # save_button = tk.Button(root, text='Screenshot', relief=RIDGE, bg='white', font='Verdana 14', command=save_frame)
    # save_button.place(x=g_w - 200, y=box_h + 220, width=150, height=50)


def update_duration(event):
    """ updates the duration after finding the duration """
    end_time["text"] = str(datetime.timedelta(seconds=vid_player.duration()))
    progress_slider["to"] = int(vid_player.duration() * vid_player.frame_rate())


def update_scale(event):
    global action, sentence, script, instruction, language
    global anno_img_name, end_anno_time, bg_img, anno_type
    global x1, x2, y1, y2
    t = vid_player.current_duration()
    second, act, eng_comment, can_comment, instruction = line_segment(script[0])
    if 1 < t - second:
        if len(script) > 1:
            script.pop(0)
            second, act, eng_comment, can_comment, instruction = line_segment(script[0])

    while t - second > 1:
        script.pop(0)
        second, act, eng_comment, can_comment, instruction = line_segment(script[0])

    if action:
        if 0 < t - second <= 1:
            if language == 'cantonese':
                write_action = threading.Thread(target=translate_action, args=(second, act))
                write_action.start()
            else:
                action_text.insert(tk.END, str(second) + 's ' + ': ' + act + '\n')

    if sentence:
        if 0 < t - second <= 1:
            if language == 'cantonese':
                sentence_text.insert(tk.END, str(second) + 's ' + ': ')
                print_sentense = threading.Thread(target=comment_sentense, args=(language, can_comment))
                print_sentense.start()
                commentary(can_comment)
            elif language == 'english':
                sentence_text.insert(tk.END, str(second) + 's ' + ': ')
                print_sentense = threading.Thread(target=comment_sentense, args=(language, eng_comment))
                print_sentense.start()
                commentary(eng_comment)

    if instruction != '' and 0 < t - second <= 1:
        if instruction[0] == "f":
            anno_type, anno_img_name, anno_time = instruction.split()
        elif instruction[0] == "s":
            anno_type, x1, x2, y1, y2, anno_time = instruction.split()
            x1,x2,y1,y2 = int(x1), int(x2), int(y1), int(y2)
        end_anno_time = t + float(anno_time)
    pass


def update_frame(event):
    global obj_det, script, augment
    global anno_img_name, end_anno_time, bg_img, anno_type
    global x1, x2, y1, y2
    progress_slider.set(vid_player.current_frame())
    t = vid_player.current_duration()
    img_after = vid_player.frame_img().copy()

    if augment and t < end_anno_time:
        if anno_type == 'f':
            if (vid_player.current_frame() % 15) > 7:
                img_after = additional_bg_information(img_after, anno_img_name, anno_img_name[:-4]+'_black.png', 0.20)
                # img_after = additional_information(img_after, anno_img_name[:-4]+'_black.png', 0.22)
            else:
                img_after = additional_bg_information(img_after, '', anno_img_name[:-4] + '_black.png', 0.20)
                # img_after = additional_information(img_after, anno_img_name, 0.22)
        if anno_type == 's':
            img_after = numpy.asarray(img_after)
            img_superres = img_after[x1:x2, y1:y2]
            img_superres = sr.upsample(img_superres)
            img_superres = cv2.resize(img_superres, (int((y2-y1)*1.45), int((x2-x1)*1.45)), interpolation=cv2.INTER_NEAREST)
            img_superres = cv2.rectangle(img_superres,(1,1),(int((y2-y1)*1.45)-1, int((x2-x1)*1.45)-1),5)
            img_superres = Image.fromarray(img_superres)
            img_after = Image.fromarray(img_after)
            img_after = add_transparent(img_after, img_superres, (int(y1*0.8), int(x1*0.8)))

    if obj_det:
        img_after = numpy.asarray(img_after)
        result = detect.detect_image(model, img_after)
        img_after = draw_box(img_after, result, colors)
        img_after = Image.fromarray(img_after)

    if t > end_anno_time:
        end_anno_time = 0

    img_after = ImageTk.PhotoImage(img_after)
    processed_video.config(image=img_after)
    processed_video.image = img_after


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


def translate_action(second, words):
    action_text.insert(tk.END, str(second) + 's ' + ': ' + eng2zh(words) + '\n')


def load_video(evt):
    """ loads the video """
    w = evt.widget  # get widget that call this function
    index = int(w.curselection()[0])  # get the index of the object clicked
    file_path = 'Video/' + w.get(index)  # get the name accroding to the index

    global anno_img_name, script, bg_img, anno_type, end_anno_time, x1, x2, y1, y2
    anno_img_name, script, bg_img, anno_type = '', '', '', ''
    end_anno_time = 0
    x1, x2, y1, y2 = 0, 0, 0, 0
    # file_path = filedialog.askopenfilename()

    if file_path:
        vid_player.load(file_path)

        progress_slider.config(to=0, from_=0)
        progress_slider.set(0)

        vid_player.play()
        play_pause_btn["text"] = "Pause"
        play_pause_btn.config(bg="red")

    for name in script_list:
        if w.get(index)[:-4] in name:
            with open('script/' + name, encoding="utf-8") as file:
                script = file.readlines()

    action_text.delete('1.0', tk.END)
    sentence_text.delete('1.0', tk.END)


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


def augment_bool():
    global augment
    augment = not augment
    if augment:
        augment_button.config(bg='red')
        augment_button["text"] = 'Remove augmentation'
    else:
        augment_button.config(bg='#DDDDDD')
        augment_button["text"] = 'Add augmentation'


def video_ended(event):
    """ handle video ended """
    progress_slider.set(progress_slider["to"])
    play_pause_btn["text"] = "Play"


def act_reg_bool():
    global action
    action = not action
    if action:
        action_rec_button.config(bg='red')
        action_rec_button["text"] = 'Stop Action Recognition'
    else:
        action_rec_button.config(bg='#DDDDDD')
        action_rec_button["text"] = 'Start Action Recognition'


def sentence_bool():
    global sentence
    sentence = not sentence
    if sentence:
        sentence_produce_button.config(bg='red')
        sentence_produce_button["text"] = 'Stop Sentence Produce'
    else:
        sentence_produce_button.config(bg='#DDDDDD')
        sentence_produce_button["text"] = 'Start Sentence Produce'


def voice_list():
    options = ['Chinese', 'English']
    language = tk.StringVar(root)
    language.set(options[0])
    voices_list = tk.OptionMenu(root, language, *options)  # Set a list
    voices_list.place(x=150 + button_w + 60 + sentence_w, y=box_h + 150 + button_h, width=130, height=30)
    voices_list.configure(font=('Arial', 14))
    voices_list['menu'].configure(font=('Arial', 14))
    language.trace("w", lambda *args: choose_language(language.get()))


def choose_language(lan):
    global language
    # 'Chinese', 'English'
    if lan == 'Chinese':
        lan = 'HongKong'
    if lan == 'HongKong':
        language = 'cantonese'
    elif lan == 'English':
        language = 'english'
    try:
        voices = tts.getProperty('voices')
        for i in range(len(voices)):
            if lan in voices[i].name:
                tts.setProperty('voice', voices[i].id)
                action_text.insert(tk.END, language + ' selected\n')
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


def print_list():
    video_list = tk.Listbox(bg='white', relief=SUNKEN)  # Set a list
    video_list.place(x=15, y=80, width=110)  # Set position
    for i, name in enumerate(list):  # Enumerate: return [index, content]
        video_list.insert(i, name)  # List name w.r.t. index and name
    video_list.bind('<<ListboxSelect>>', load_video)  # When selected, run onselect\


if __name__ == "__main__":
    anno_img_name, script, bg_img, anno_type, instruction = '', '', '', '', ''
    sentence, action, augment = False, False, False
    language = 'english'
    script_list = call_from_folder("script")
    end_anno_time = 0
    x1, x2, y1, y2 = 0, 0, 0, 0
    lines = []
    # INIT TKINTER & UTILS:
    while True:
        root = tk.Tk()
        root.title("Tkinter media")
        # root.attributes('-zoomed', True)  # Ubuntu
        root.state('zoomed')  # Window
        root.resizable(0, 0)  # Window
        root.update()

        root_h = root.winfo_height()
        root_w = root.winfo_width()

        box_w = (root_w - 200) / 2  # video box width
        box_h = box_w * 9 / 16  # video box height
        # load_btn = tk.Button(root, text="Load", command=load_video)
        # load_btn.pack()
        load_widget()
        list = call_from_folder("Video")  # Find all files in the folder
        print_list()  # List out all files

        vid_player = TkinterVideo(scaled=True, pre_load=False, master=root, bg='white', relief=SUNKEN)
        vid_player.place(x=150, y=80, width=box_w, height=box_h)

        processed_video = tk.Label(root, bg='white', relief=SUNKEN)
        processed_video.place(x=150 + 20 + box_w, y=80, width=box_w, height=box_h)

        play_pause_btn = tk.Button(root, text="Play", command=play_pause, bg="grey", font=('bold', 16))
        play_pause_btn.place(x=150, y=80 + box_h + 40, width=120, height=30)

        skip_min_5sec = tk.Button(root, text="Skip -5 sec", command=lambda: skip(-5 * 25))
        skip_min_5sec.place(x=70, y=80 + box_h + 20)

        skip_plus_5sec = tk.Button(root, text="Skip +5 sec", command=lambda: skip(5 * 25))
        skip_plus_5sec.place(x=150 + box_w, y=80 + box_h + 20)

        start_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        start_time.place(x=90, y=80 + box_h)

        end_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        end_time.place(x=150 + box_w, y=80 + box_h)

        progress_slider = tk.Scale(root, from_=0, to=0, orient="horizontal", showvalue=0, command=seek)
        progress_slider.place(x=150, y=80 + box_h, width=box_w)

        vid_player.bind("<<Duration>>", update_duration)
        vid_player.bind("<<SecondChanged>>", update_scale)
        vid_player.bind("<<FrameChanged>>", update_frame)
        vid_player.bind("<<Ended>>", video_ended)

        obj_det = False
        process_btn = tk.Button(root, text="Object Detect", command=detect_bool, bg="#DDDDDD", font=20)
        process_btn.place(x=150 + box_w + 300, y=80 + box_h + 30, width=150)

        augment_button = tk.Button(root, text='Add augmentation', command=augment_bool, bg='#DDDDDD', font=20)
        augment_button.place(x=150 + box_w + 480, y=80 + box_h + 30, width=150)

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

        var_action = tk.StringVar()
        action_rec_button = tk.Button(root, relief=RIDGE, bg='#DDDDDD', font=('bold', 14),
                                      text='Start Action Recognition',
                                      command=act_reg_bool)
        action_rec_button.place(x=150 + button_w + 150, y=box_h + 170)

        var_sentence = tk.StringVar()
        sentence_produce_button = tk.Button(root, relief=RIDGE, bg='#DDDDDD', font=('bold', 14),
                                            text='Start Sentences Produce',
                                            command=sentence_bool)
        sentence_produce_button.place(x=150 + button_w + 400, y=box_h + 170)

        voice_list()
        tts = pyttsx3.init()
        rate = tts.getProperty('rate')
        tts.setProperty('rate', rate - 20)
        voices = tts.getProperty('voices')
        sentence_text.insert(tk.END, 'This computer have installed: ')
        for i in range(len(voices)):
            sentence_text.insert(tk.END, '\n' + voices[i].name)
        choose_language('HongKong')

        class_no = sum(1 for line in open('model/coco.name'))
        colors = create_color_by_class(class_no)
        model = models.load_model("model/yolov3.cfg", "model/yolov3.weights")
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        path = 'model/FSRCNN-small_x2.pb'
        sr.readModel(path)
        sr.setModel("fsrcnn", 2)
        break

root.mainloop()
