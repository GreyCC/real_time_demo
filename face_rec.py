import os
import face_recognition


def load_players(folder_name):
    players_face = []
    players_encode = []
    players_list = []
    file_list = os.listdir(folder_name)

    for name in file_list:
        players_face.append(face_recognition.load_image_file(folder_name + '/' + name))
        try:
            players_encode.append(face_recognition.face_encodings(players_face[-1],face_recognition.face_locations(players_face[-1]))[0])
            players_list.append(name)
        except IndexError:  # Delete no face img
            pass
    return players_encode, players_list

#---------------------------Reconite face----------------------------------

# known_face = []
# known_face_encode = []
# img_list = []
# file_list = os.listdir('image')
#
# for name in file_list:
#     #print(name)
#     known_face.append(face_recognition.load_image_file('image/' + name))
#     try:
#         known_face_encode.append(face_recognition.face_encodings(known_face[-1])[0])
#         img_list.append(name)
#     except IndexError: #Delete no face img
#         pass
# known_face.clear()
# print(img_list)
# unknown_face = face_recognition.load_image_file('unknown.png')
# unknown_face_encode = face_recognition.face_encodings(unknown_face)[0]
#
# # for i in known_face_encode:
# results = face_recognition.face_distance(known_face_encode, unknown_face_encode)
# print(results)

# for i in range(3):
#     if results[i]:
#         print(img_list[i])

#-------------------------------------------------------------------------


# results = face_recognition.compare_faces([known_face_encode], unknown_face_encode)
#
# if results[0]:
#     print("It's a picture of Fellaini!")
# else:
#     print("It's not a picture of Fellaini!")


#---------------------------Face Detection----------------------------------

# known_face = face_recognition.load_image_file("image/no_face.jpg")
# known_face_encode = face_recognition.face_locations(known_face)
#
# if known_face_encode == []:
#     print('no face')
# else:
#     for (top, right, bottom, left) in known_face_encode:
#         cv2.rectangle(known_face, (left, top), (right, bottom), (0, 0, 255), 2)
#
#     cv2.imshow('Face Location', known_face)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()





# # Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file("biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
#
# # Create arrays of known face encodings and their names
# known_face_encodings = [
#     obama_face_encoding,
#     biden_face_encoding
# ]
# known_face_names = [
#     "Barack Obama",
#     "Joe Biden"
# ]
#
# # Initialize some variables
# face_locations = []
# face_encodings = []
# face_names = []
# process_this_frame = True
#
# while True:
#     # Grab a single frame of video
#     ret, frame = video_capture.read()
#
#     # Resize frame of video to 1/4 size for faster face recognition processing
#     small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#
#     # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#     rgb_small_frame = small_frame[:, :, ::-1]
#
#     # Only process every other frame of video to save time
#     if process_this_frame:
#         # Find all the faces and face encodings in the current frame of video
#         face_locations = face_recognition.face_locations(rgb_small_frame, model='cnn')
#         face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
#
#         face_names = []
#         for face_encoding in face_encodings:
#             # See if the face is a match for the known face(s)
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"
#
#             # # If a match was found in known_face_encodings, just use the first one.
#             # if True in matches:
#             #     first_match_index = matches.index(True)
#             #     name = known_face_names[first_match_index]
#
#             # Or instead, use the known face with the smallest distance to the new face
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#             best_match_index = np.argmin(face_distances)
#             if matches[best_match_index]:
#                 name = known_face_names[best_match_index]
#
#             face_names.append(name)
#
#     process_this_frame = not process_this_frame
#
#     # Display the results
#     for (top, right, bottom, left), name in zip(face_locations, face_names):
#         # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#         top *= 4
#         right *= 4
#         bottom *= 4
#         left *= 4
#
#         # Draw a box around the face
#         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#
#         # Draw a label with a name below the face
#         cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#
#     # Display the resulting image
#     cv2.imshow('Video', frame)
#
#     # Hit 'q' on the keyboard to quit!
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Release handle to the webcam
# video_capture.release()
# cv2.destroyAllWindows()
