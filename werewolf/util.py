# -*- encoding: utf-8 -*-
import random
import math
from collections import Counter

class Util(object):
    @staticmethod
    def shuffle(_list):
        return sorted(_list, key=lambda *args: random.random())

    @staticmethod
    def select_most_voted(_list):
        u""" 最頻値（複数ある場合はランダムで1つ選択）を返す """
        if not _list:
            return None
        cnt = Counter(_list)
        max_val = cnt.most_common(1)[0][1]
        most_voted = [k for k, c in cnt.iteritems() if c == max_val]
        random.shuffle(most_voted)
        return most_voted[0]

    @staticmethod
    def hsv_random_color(saturation=0.7, value=0.7):
        """
        get random color based on same S and V .
        See: http://en.wikipedia.org/wiki/HSL_and_HSV#From_HSV
        """
        hue = random.random() * 360
        hue2 = hue / 60
        chroma = value * saturation

        s = saturation
        v = value
        c = chroma
        x = chroma * (1 - math.fabs(math.fmod(hue2, 2) - 1))

        add_two_list = lambda x, y: [x[i] + y[i] for i in range(len(x))]

        if hue2 < 1:
            rgb = add_two_list([c, x, 0], [v-c, v-c, v-c])
        elif hue2 < 2:
            rgb = add_two_list([x, c, 0], [v-c, v-c, v-c])
        elif hue2 < 3:
            rgb = add_two_list([0, c, x], [v-c, v-c, v-c])
        elif hue2 < 4:
            rgb = add_two_list([0, x, c], [v-c, v-c, v-c])
        elif hue2 < 5:
            rgb = add_two_list([x, 0, c], [v-c, v-c, v-c])
        elif hue2 < 6:
            rgb = add_two_list([c, 0, x], [v-c, v-c, v-c])
        else:
            rgb = [0, 0, 0]

        rgb = [x*256 for x in rgb]

        return "#%02x%02x%02x" % tuple(rgb)

if __name__=="__main__":
    print Util.hsv_random_color()
    print Util.select_most_voted([1, 2, 2, 3, 3])
