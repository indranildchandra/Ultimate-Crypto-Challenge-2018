import numpy as np
import re
import itertools
from collections import Counter
import tqdm

def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

# def load_data_and_labels(positive_data_file, negative_data_file):
def load_data_and_labels(fileList):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # # Load data from files
    # positive_examples = list(open(positive_data_file, "r").readlines())
    # positive_examples = [s.strip() for s in positive_examples]
    # negative_examples = list(open(negative_data_file, "r").readlines())
    # negative_examples = [s.strip() for s in negative_examples]
    # # Split by words
    # x_text = positive_examples + negative_examples
    # x_text = [clean_str(sent) for sent in x_text]
    # # Generate labels
    # positive_labels = [[0, 1] for _ in positive_examples]
    # negative_labels = [[1, 0] for _ in negative_examples]
    # y = np.concatenate([positive_labels, negative_labels], 0)

    # print(x_text)
    # print(y)
    # return [x_text, y]

    # Load data from files



    # body1 = list(open(data_file1, "r").readlines())
    # if data_file2 is not None:
    #     body2 = list(open(data_file2, "r").readlines())
    # body = [s.strip() for s in body]

    x_text = []
    y = []

    noOfLabels = len(fileList)
    curLabel = 0
    for file in fileList:
        body = list(open(file, "r").readlines())
        for line in tqdm.tqdm(body):
            mail = line.strip()
            mail = re.sub(r'\w*@\w*.\w{2,3}', 'properemail ', mail) #remove emails
            mail = re.sub(r'[\d]+', 'purenumber ', mail) #remove numbers
            mail = re.sub(r'\w*[\d@$\t-]\w*', 'specialcharword ', mail) #remove words containing numbers and special characters
            mail = re.sub(r'[-_|]', ' ', mail) #remove any dashes
            mail = re.sub(r'[.]', '. ', mail) #append . with space
            #remove any extra spaces
            mail = mail.split()
            mail = " ".join(mail)

            x_text.append(mail)

            arr = []
            for _ in range(noOfLabels):
                arr.append(0)
            arr[curLabel] = 1

            if len(y) == 0:
                y = [arr]
            else:
                y = np.concatenate([y,[arr]],0)  

        curLabel += 1
                      
    # for line in body1:
    #     x_text.append(line)
    #     if len(y) == 0:
    #         y = [[1,0]]
    #     else:
    #         y = np.concatenate([y,[[1,0]]],0)

    # if data_file2 is not None:
    #     for line in body2:
    #         x_text.append(line)
    #         if len(y) == 0:
    #             y = [[0,1]]
    #         else:
    #             y = np.concatenate([y,[[0,1]]],0)



    # # Generate labels
    # labels_arr = open(labels_file, "r").readlines()
    # labels = []
    # labels2id = {}
    # for i in labels_arr:
    #     if i not in labels:
    #         labels.append(i)
    #         labels2id[i] = len(labels)

    # # print("labels")
    # # print(labels)
    # # print("labels2id")
    # # print(labels2id)

    # y = []
    # label_arr_index = -1
    # for i in body:
    #     if i == "Start===":
    #         label_arr_index += 1
    #         continue
    #     if i == "\n" or i == "":
    #         continue
    #     if label_arr_index > -1:
    #         x_text.append(clean_str(i))

    #         arr = []
    #         for _ in range(len(labels)):
    #             arr.append(0)

    #         # print("labels_arr[label_arr_index]")
    #         # print(labels_arr[label_arr_index])
    #         # print("labels2id[labels_arr[label_arr_index]]-1")
    #         # print(labels2id[labels_arr[label_arr_index]]-1)
    #         arr[labels2id[labels_arr[label_arr_index]]-1] = 1
    #         if len(y) == 0:
    #             y = [arr]
    #         else:
    #             y = np.concatenate([y,[arr]],0)

    print(x_text)
    print(y)

    return [x_text, y]


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
