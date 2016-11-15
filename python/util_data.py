import os
import re
import glob
import nltk
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

def download_babi(data_dir):
        babi_dir = os.path.join(data_dir, 'babi')
        tasks_file = os.path.join(data_dir, "tasks.tar.gz")

        if not os.path.exists(babi_dir):
                os.makedirs(babi_dir)

        if not os.path.exists(tasks_file):
                os.system("wget -O {} http://www.thespermwhale.com/jaseweston/babi/tasks_1-20_v1-2.tar.gz".format(tasks_file))

        os.system("tar -xzf {} -C {} --strip-components 1".format(tasks_file, babi_dir))

def load_babi(data_dir):
        babi_en10k_dir = os.path.join(data_dir, 'babi/en-10k/*')
        
        unique_words = set()
        unique_answers = set()
        for file in glob.glob(babi_en10k_dir):
                stories = []
                with open(file, 'r') as f:
                        lines = [str(re.sub("\d", "", line)).strip() for line in f.readlines()]
                        story = []
                        for line in lines:
                                line = line.replace(",", " , ").replace("?", " ? ")
                                line = line.replace(".", " . ").replace(",", " , ").replace('\'','')
                                
                                if "\t" not in line:
                                        # not a question
                                        words = line.split()
                                        unique_words = unique_words.union(set(words))
                                        story.extend(words)
                                else:
                                        # question
                                        [line, answer] = line.split("\t")
                                        words = line.split()
                                        unique_words = unique_words.union(set(words))
                                        unique_answers = unique_answers.union(set([answer]))
                                        story.extend(words)
                                        this_story = {
                                                        "seq": story,
                                                        "answer": answer
                                        }
                                        stories.append(this_story)
                                        story = []
                break

        longest_story = max(stories, key=lambda s: len(s["seq"]))
        longest_story_len = len(longest_story["seq"])
        print("Input will be a sequence of {} words, "\
                  "padding by zeros at the beginning when "\
                  "needed.".format(len(longest_story["seq"])))

        num_words = len(unique_words)
        num_answers = len(unique_answers)
        print("There are {} unique words, which will be mapped to one-hot encoded vectors.".format(num_words))
        print("There are {} unique answers, which will be mapped to one-hot encoded vectors.".format(num_answers))
        lb = preprocessing.LabelBinarizer()
        word_encoder = lb.fit(list(unique_words))

        lba = preprocessing.LabelBinarizer()
        answer_encoder = lba.fit(list(unique_answers))

        def pad_and_encode_seq(seq, seq_len=longest_story_len):
                if len(seq) > seq_len:
                        raise RuntimeError("Should never see a sequence greater than {} length".format(seq_len))
                return word_encoder.transform((['' for i in range(seq_len-len(seq))]) + seq)

        print()
        print("Encoding sequences...")
        X = []
        y = []
        from collections import defaultdict

        for story in stories:
                X.append(np.array(pad_and_encode_seq(story["seq"])))
                y.append(answer_encoder.transform([story["answer"]])[0])
           
        X = np.array(X)
        y = np.array(y)

        print()
        print("X:", X.shape)
        print("y:", y.shape)
        print()

        return X, y