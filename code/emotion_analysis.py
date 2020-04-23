import csv
import re
import jieba
import numpy as np
from keras import Input, Model
from keras.layers import Embedding, GRU, Dropout, Dense
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras_preprocessing.text import Tokenizer
from keras_self_attention import SeqSelfAttention
import matplotlib.pyplot as plt


# 读取文件信息
def get_csv_message():
    # 存储文本数据
    data = []
    # 存储标签
    label = []
    with open('data.csv', 'r', encoding='UTF-8') as file:
        file = csv.reader(file)
        # 越过第一行
        for row in file:
            break
        # 提取对应列的信息
        for row in file:
            # 数据清洗 []切割需要放在里面
            text = re.split('[，。？“”【】（）！#@?]', row[-1])
            # 去除列表空元素
            while '' in text:
                text.remove('')
            # 添加进列表
            data.extend(text)
            label.append(int(row[0]))
        return data, label


# 数据预处理
def data_preprocess(text_data, text_label):
    text_sentence = []
    temp = []
    for i in text_data:
        k = jieba.lcut(i)
        text_sentence.append(k)
        temp += [j for j in k if j not in k]
    # 构建词典
    tokenizer = Tokenizer(num_words=len(temp))
    tokenizer.fit_on_texts(text_sentence)
    # 文本序列化
    text_sentence = tokenizer.texts_to_sequences(text_sentence)
    text_sentence = pad_sequences(text_sentence, maxlen=64, padding='post')
    # 标签
    text_label = to_categorical(text_label)
    # 提取预训练好的词向量
    embedding_matrix = np.zeros((len(tokenizer.word_index) + 1, 60), dtype=np.float32)
    file = open('wiki.zh.text.vector', encoding='utf-8')
    file = file.readlines()
    for text in file:
        text = text.split()
        if text[0] in temp:
            embedding_matrix[tokenizer.word_index[text[0]]] = text[1:]

    return text_sentence, text_label, tokenizer, embedding_matrix


# 构建模型
def model(train_data, train_label, tokenizer, embedding_matrix):
    x = Input(shape=(20,))
    embed = Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=60, input_length=64, weights=[embedding_matrix], mask_zero=True)(x)
    h = GRU(64)(embed)
    h = SeqSelfAttention(attention_activation='softmax')(h)
    h = Dense(10, activation='softmax')(h)
    model = Model(inputs=x, outputs=h)
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    history = model.fit(x=train_data, y=train_label, batch_size=64, epochs=10, validation_split=0.2)
    # y_pred = model.predict(vaild_data)

    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model acc')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()
    # 汇总损失函数历史数据
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()


if __name__ == '__main__':
    data, label = get_csv_message()
    text_sentence, text_label, tokenizer, embedding_matrix = data_preprocess(data, label)
    model(text_sentence, text_label, tokenizer, embedding_matrix)