# -*- coding: utf-8 -*-
import random
from collections import Counter


def shuffle(_list):
    return sorted(_list, key=lambda *args: random.random())


def select_most_voted(_list):
    u""" 最頻値（複数ある場合はランダムで1つ選択）を返す """
    if not _list:
        return None
    cnt = Counter(_list)
    max_val = cnt.most_common(1)[0][1]
    most_voted = [k for k, c in cnt.iteritems() if c == max_val]
    random.shuffle(most_voted)
    return most_voted[0]


if __name__=="__main__":
    print select_most_voted([1, 2, 2, 3, 3])
