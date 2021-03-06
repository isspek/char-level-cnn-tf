# based on ideas from https://github.com/dennybritz/cnn-text-classification-tf

import numpy as np
import json
import tensorflow as tf
from config import Config

config = Config()
params = config.params
sequence_max_length = params['model']['sequence_max_length']
alphabet = params['alphabet']

def quantize(x, alphabet):
    temp = []
    for text in x:
        text_end_extracted = extract_end(list(text.lower()))
        padded = pad_sentence(text_end_extracted)
        text_int8_repr = string_to_int8_conversion(padded, alphabet)
        temp.append(text_int8_repr)
    xq = np.array(temp, dtype=np.int8)
    return xq

def extract_end(char_seq):
    if len(char_seq) > sequence_max_length:
        char_seq = char_seq[-sequence_max_length:]
    return char_seq


def pad_sentence(char_seq, padding_char=" "):
    char_seq_length = sequence_max_length
    num_padding = char_seq_length - len(char_seq)
    new_char_seq = char_seq + [padding_char] * num_padding
    return new_char_seq


def string_to_int8_conversion(char_seq, alphabet):
    x = np.array([alphabet.find(char) for char in char_seq], dtype=np.int8)
    return x


def get_batched_one_hot(char_seqs_indices, labels, start_index, end_index):
    x_batch = char_seqs_indices[start_index:end_index]
    y_batch = labels[start_index:end_index]
    x_batch_one_hot = np.zeros(shape=[len(x_batch), len(alphabet), len(x_batch[0]), 1])
    for example_i, char_seq_indices in enumerate(x_batch):
        for char_pos_in_seq, char_seq_char_ind in enumerate(char_seq_indices):
            if char_seq_char_ind != -1:
                x_batch_one_hot[example_i][char_seq_char_ind][char_pos_in_seq][0] = 1
    return [x_batch_one_hot, y_batch]


def load_data():
    # TODO Add the new line character later for the yelp'cause it's a multi-line review
#     examples, labels = load_yelp(alphabet)
#     x = np.array(examples, dtype=np.int8)
#     y = np.array(labels, dtype=np.int8)
    
    x = np.load(params['data']['train'])
    x = quantize(x,alphabet)
    y = np.load(params['data']['label'])
    y = tf.keras.utils.to_categorical(y)
    print("x_char_seq_ind=" + str(x.shape))
    print("y shape=" + str(y.shape))
    return [x, y]


def batch_iter(x, y, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    # data = np.array(data)
    data_size = len(x)
    num_batches_per_epoch = int(data_size/batch_size) + 1
    for epoch in range(num_epochs):
        print("In epoch >> " + str(epoch + 1))
        print("num batches per epoch is: " + str(num_batches_per_epoch))
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            x_shuffled = x[shuffle_indices]
            y_shuffled = y[shuffle_indices]
        else:
            x_shuffled = x
            y_shuffled = y
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            x_batch, y_batch = get_batched_one_hot(x_shuffled, y_shuffled, start_index, end_index)
            batch = list(zip(x_batch, y_batch))
            yield batch
