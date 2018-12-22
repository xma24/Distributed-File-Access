from multiprocessing import Process, Pipe
import os
import threading
import time
import numpy as np

process_number = 3
event_number = 3
file_name = "shared_file.txt"
total_requests = 3
shared_number = 0

with open(file_name, 'w') as f_shared:
    f_shared.write(str(shared_number) + ",")


def sending_events_thread(pid, ok_list, pipe_list_local, process_id, sending_indicator, file_name, request_record,
                          start, record_message):
    print("P%s:PID%s " % (str(process_id), str(pid)))

    stop_sending = 0
    while True:
        if stop_sending == 0:
            time.sleep(3)

            if sending_indicator[0] == 1:
                request_time = time.time()
                message_to_send = create_event(pid, file_name, request_time, process_id)
                ok_list[process_id - 1] = 1
                send_messages(pipe_list_local, process_id, message_to_send)
                if not len(record_message) == 0:
                    del record_message[0]
                    record_message.append(message_to_send)
                else:
                    record_message.append(message_to_send)

                if request_record[0] >= total_requests - 1:
                    stop_sending = 1
                else:
                    request_record[0] += 1
                sending_indicator[0] = 0


def create_event(pid, file_name, time_stamp, process_id):
    process_name = str(pid) + "." + str(process_id)
    source = file_name
    timestamp = str(time_stamp)
    return process_name, source, timestamp


def send_messages(pipe_list_local, process_id, event):
    if process_id == 1:
        pipe_list_local[0][0].send(event)
        pipe_list_local[2][0].send(event)
    elif process_id == 2:
        pipe_list_local[0][1].send(event)
        pipe_list_local[1][0].send(event)
    elif process_id == 3:
        pipe_list_local[2][1].send(event)
        pipe_list_local[1][1].send(event)


def receive_messages(pipe_list_local, process_id, start):
    received_events = []
    received_ok = []
    time.sleep(9)
    print("")
    print("process_id: ", process_id)

    if start[0] == 1:
        if process_id == 1:
            recevied_message_21 = pipe_list_local[0][0].recv()
            if len(recevied_message_21) == 1:
                received_ok.append(recevied_message_21)
            elif len(recevied_message_21) == 3:
                received_events.append(recevied_message_21)

            recevied_message_31 = pipe_list_local[2][0].recv()
            if len(recevied_message_31) == 1:
                received_ok.append(recevied_message_31)
            elif len(recevied_message_31) == 3:
                received_events.append(recevied_message_31)
        elif process_id == 2:
            recevied_message_12 = pipe_list_local[0][1].recv()
            if len(recevied_message_12) == 1:
                received_ok.append(recevied_message_12)
            elif len(recevied_message_12) == 3:
                received_events.append(recevied_message_12)
        elif process_id == 3:
            recevied_message_13 = pipe_list_local[2][1].recv()
            if len(recevied_message_13) == 1:
                received_ok.append(recevied_message_13)
            elif len(recevied_message_13) == 3:
                received_events.append(recevied_message_13)
        else:
            print("Process ID is not valid.")

    elif start[0] == 0:
        if process_id == 1:
            recevied_message_21 = pipe_list_local[0][0].recv()
            if len(recevied_message_21) == 1:
                received_ok.append(recevied_message_21)
            elif len(recevied_message_21) == 3:
                received_events.append(recevied_message_21)

            recevied_message_31 = pipe_list_local[2][0].recv()
            if len(recevied_message_31) == 1:
                received_ok.append(recevied_message_31)
            elif len(recevied_message_31) == 3:
                received_events.append(recevied_message_31)
        elif process_id == 2:
            recevied_message_12 = pipe_list_local[0][1].recv()
            if len(recevied_message_12) == 1:
                received_ok.append(recevied_message_12)
            elif len(recevied_message_12) == 3:
                received_events.append(recevied_message_12)

            recevied_message_32 = pipe_list_local[1][0].recv()
            if len(recevied_message_32) == 1:
                received_ok.append(recevied_message_32)
            elif len(recevied_message_32) == 3:
                received_events.append(recevied_message_32)
        elif process_id == 3:
            recevied_message_13 = pipe_list_local[2][1].recv()
            if len(recevied_message_13) == 1:
                received_ok.append(recevied_message_13)
            elif len(recevied_message_13) == 3:
                received_events.append(recevied_message_13)

            recevied_message_23 = pipe_list_local[1][1].recv()
            if len(recevied_message_23) == 1:
                received_ok.append(recevied_message_23)
            elif len(recevied_message_23) == 3:
                received_events.append(recevied_message_23)
        else:
            print("Process ID is not valid.")
    return received_events, received_ok


def send_ok(pipe_list_local, send_process_id, receive_process_id):
    ok_message = (str(send_process_id) + "." + "ok",)
    if send_process_id == 1:
        if receive_process_id == 2:
            pipe_list_local[0][0].send(ok_message)
        elif receive_process_id == 3:
            pipe_list_local[2][0].send(ok_message)
    elif send_process_id == 2:
        if receive_process_id == 1:
            pipe_list_local[0][1].send(ok_message)
        elif receive_process_id == 3:
            pipe_list_local[1][0].send(ok_message)
    elif send_process_id == 3:
        if receive_process_id == 1:
            pipe_list_local[2][1].send(ok_message)
        elif receive_process_id == 2:
            pipe_list_local[1][1].send(ok_message)


def add_number_to_file(file_name):
    with open(file_name, 'r') as f_add_number_read:
        previous_str = f_add_number_read.read()

    with open(file_name, 'a') as f_add_number_write:
        previous_list = previous_str.split(",")
        new_number = int(previous_list[-2]) + 1
        append_str = str(new_number) + ","
        f_add_number_write.write(append_str)
        print("current string in the file: ", previous_str + append_str)


def communication_thread(pid, pipe_list_local, process_id, sending_indicator, ok_list, start, record_message,
                         send_ok_index_list):
    receive_number = 1
    while True:
        received_events, received_ok = receive_messages(pipe_list_local, process_id, start)

        receive_number += 1
        if receive_number == total_requests + 1:
            start[0] = 0
        else:
            start[0] = 0
        print("received events " + str(pid), received_events)
        print("received oks " + str(pid), received_ok)
        print("record_message: ", record_message)
        current_time = float(record_message[0][2])

        if not len(received_events) == 0:
            for event_index in range(len(received_events)):
                receive_process_id = int(received_events[event_index][0].split(".")[1])
                if float(current_time) > float(received_events[event_index][2]):
                    send_ok(pipe_list_local, process_id, receive_process_id)
                elif float(current_time) < float(received_events[event_index][2]):
                    send_ok_index_list.append(receive_process_id)
        print("send_ok_index_list: ", send_ok_index_list)

        if not len(received_ok) == 0:
            for ok_event in range(len(received_ok)):
                received_ok_index = int(received_ok[ok_event][0].split(".")[0]) - 1
                ok_list[received_ok_index] = 1

        while not np.mean(ok_list) == 1:
            received_events, received_ok = receive_messages(pipe_list_local, process_id, start)

            if not len(received_ok) == 0:
                for ok_event in range(len(received_ok)):
                    received_ok_index = int(received_ok[ok_event][0].split(".")[0]) - 1
                    ok_list[received_ok_index] = 1

        if np.mean(ok_list) == 1:
            add_number_to_file(file_name)

            for ok_i in range(len(ok_list)):
                ok_list[ok_i] = 0

            for send_ok_i in range(len(send_ok_index_list)):
                send_ok(pipe_list_local, process_id, send_ok_index_list[send_ok_i])

            lenght_of_send_ok_index_list = len(send_ok_index_list)
            for send_ok_i in range(lenght_of_send_ok_index_list):
                del send_ok_index_list[0]

            sending_indicator[0] = 1


def process1(pipe_list_local):
    current_pid = os.getpid()
    process_id = 1
    record_message = []
    sending_indicator = [1]
    ok_list = [0, 0, 0]
    start = [0]
    request_record = [0]
    send_ok_index_list = []

    thread_send = threading.Thread(target=sending_events_thread, args=(
        current_pid, ok_list, pipe_list_local, process_id,
        sending_indicator, file_name, request_record, start, record_message))

    thread_communicate = threading.Thread(target=communication_thread,
                                          args=(current_pid,
                                                pipe_list_local, process_id, sending_indicator,
                                                ok_list, start, record_message, send_ok_index_list))

    thread_send.start()
    thread_communicate.start()

    thread_send.join()
    thread_communicate.join()


def process2(pipe_list_local):
    current_pid = os.getpid()
    process_id = 2
    ok_list = [0, 0, 0]
    sending_indicator = [1]
    start = [0]
    request_record = [0]
    record_message = []
    send_ok_index_list = []

    time.sleep(2)

    thread_send = threading.Thread(target=sending_events_thread, args=(
        current_pid, ok_list, pipe_list_local, process_id,
        sending_indicator, file_name, request_record, start, record_message))

    thread_communicate = threading.Thread(target=communication_thread,
                                          args=(
                                              current_pid,
                                              pipe_list_local, process_id, sending_indicator, ok_list, start,
                                              record_message, send_ok_index_list))

    thread_send.start()
    thread_communicate.start()

    thread_send.join()
    thread_communicate.join()


def process3(pipe_list_local):
    current_pid = os.getpid()
    process_id = 3
    ok_list = [0, 0, 0]
    sending_indicator = [1]
    start = [0]
    request_record = [0]
    record_message = []
    send_ok_index_list = []

    time.sleep(6)

    thread_send = threading.Thread(target=sending_events_thread, args=(
        current_pid, ok_list, pipe_list_local, process_id,
        sending_indicator, file_name, request_record, start, record_message))

    thread_communicate = threading.Thread(target=communication_thread,
                                          args=(
                                              current_pid,
                                              pipe_list_local, process_id, sending_indicator, ok_list, start,
                                              record_message, send_ok_index_list))

    thread_send.start()
    thread_communicate.start()

    thread_send.join()
    thread_communicate.join()


pipe_list = []

for pipe_index in range(process_number):
    (pipe_send, pipe_recv) = Pipe()
    pipe_list.append((pipe_send, pipe_recv))

print(pipe_list)

P1 = Process(target=process1, args=(pipe_list,))
P2 = Process(target=process2, args=(pipe_list,))
P3 = Process(target=process3, args=(pipe_list,))

P1.start()
P2.start()
P3.start()

P1.join()
P2.join()
P3.join()
