import re
from pyknp import KNP
import time
import timeout_decorator

@timeout_decorator.timeout(20)
def analyze_pas(sentence, knp):
    li = []
    result = knp.parse(sentence)
    for b in  result.bnst_list():
        match = re.search(r"<項構造:(.+)>", b.spec())
        if match:
            pas =  match.group(1)
            items = pas.split(":")
            li.append(items)
            #print(b.bnst_id, items)
    return li

def kaku_extract(li):
    word_li = []
    kaku_li = []
    syugo_li = []

    for elem in li:
        word = elem[0].split('/')[0]
        hinshi = elem[1]
        if "動" in hinshi:
            meishi = elem[2].split(';')
            for mei in meishi:
                m = mei.split('/')
                kaku = m[0]
                syugo = m[2]
                #print(word, kaku, syugo)
                if kaku == "ガ" or kaku == "ヲ" or kaku == "ニ" or kaku == "デ" or kaku == "ト" or kaku == "ヘ" or kaku == "カラ" or kaku == "ヨリ" or kaku == "マデ":    
                    #print(word, kaku, syugo)
                    word_li.append(word)
                    kaku_li.append(kaku)
                    syugo_li.append(syugo)
    
    return word_li, kaku_li, syugo_li

import sys

def check_kaku_frame(root, word_li, kaku_li, syugo_li):
    len_word = len(word_li)
    correct_num = 0
    for word, kaku, syugo in zip(word_li, kaku_li, syugo_li):
        #print(word)
        bool = False
        for i, child in enumerate(root):
            head_word = child.attrib["headword"]
            heads = head_word.split('/')
            if word in heads:    
                #print("head word:", head_word)
                for child2 in child:
                    for child3 in child2:
                        #print("格: ", child3.attrib["case"])
                        this_kaku = child3.attrib["case"]
                        components = child3.findall("component")
                        for component in components:
                            comp = component.text.split('/')[0]
                            kaku2 = kaku + "格"
                            if comp == syugo and kaku2 == this_kaku:
                                #print(kaku2, comp)
                                #print("yes")
                                bool = True
                            #print(comp)
                        #print()
                #print()
            if bool == True:
                correct_num += 1
                break
    if correct_num == len_word:
        return "yes"
    else:
        #print("correct_num", correct_num)
        return "no"

@timeout_decorator.timeout(300)
def check_kaku_frame2(root, word_li, kaku_li, syugo_li):
    len_word = len(word_li)
    correct_num = 0
    for word, kaku, syugo in zip(word_li, kaku_li, syugo_li):
        #print(word)
        bool = False
        for i, child in enumerate(root):
            head_word = child.attrib["headword"]
            heads = head_word.split('/')
            if word in heads:    
                #print("head word:", head_word)
                for child2 in child:
                    for child3 in child2:
                        for child4 in child3:
                            if int(child4.attrib["frequency"]) < 2:
                                continue
                            #print("格: ", child3.attrib["case"])
                        this_kaku = child3.attrib["case"]
                        components = child3.findall("component")
                        for component in components:
                            comp = component.text.split('/')[0]
                            kaku2 = kaku + "格"
                            if comp == syugo and kaku2 == this_kaku:
                                #print(kaku2, comp)
                                #print("yes")
                                bool = True
                            #print(comp)
                        #print()
                #print()
            if bool == True:
                correct_num += 1
                break
        if bool == False:
            break
    if correct_num == len_word:
        return "yes"
    else:
        #print("correct_num", correct_num)
        return "no"


