import re
import sys
from pyknp import KNP
import time
import timeout_decorator

#KNPで解析
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

#主語・格・述語を抽出
def kaku_extract(li):
    word_li = []
    kaku_li = []
    syugo_li = []
    
    
    #liの中身の例： ['飼う/かう', '動1', 'ガ/N/私/0;ヲ/C/猫/1']]
    for elem in li:
        word = elem[0].split('/')[0]
        hinshi = elem[1]
        if "動" in hinshi:
            meishi = elem[2].split(';')
            for mei in meishi:
                m = mei.split('/')
                kaku = m[0]
                syugo = m[2]
                #格が以下の時、述語・格・主語をそれぞれ配列に格納
                if kaku == "ガ" or kaku == "ヲ" or kaku == "ニ" or kaku == "デ" or kaku == "ト" or kaku == "ヘ" or kaku == "カラ" or kaku == "ヨリ" or kaku == "マデ":    
                    #print(word, kaku, syugo)
                    word_li.append(word)
                    kaku_li.append(kaku)
                    syugo_li.append(syugo)
    
    return word_li, kaku_li, syugo_li

#抽出した格フレームを京大のデータと照合
def check_kaku_frame(root, word_li, kaku_li, syugo_li):
    len_word = len(word_li)
    correct_num = 0
    for word, kaku, syugo in zip(word_li, kaku_li, syugo_li):
        bool = False
        for i, child in enumerate(root):
            head_word = child.attrib["headword"]
            heads = head_word.split('/')
            #同じ述語を持つ格フレームの中から、主語・格・述語が一致するものがあるかを探す
            if word in heads:    
                for child2 in child:
                    for child3 in child2:
                        this_kaku = child3.attrib["case"]
                        components = child3.findall("component")
                        for component in components:
                            comp = component.text.split('/')[0]
                            kaku2 = kaku + "格"
                            #格フレームの主語・格が京大格フレームと一致したら、boolをTrueにする
                            if comp == syugo and kaku2 == this_kaku:
                                bool = True
            #主語・格・述語が一致するものがあれば、その述語は正しいと判断し、correct_numを1増やす
            if bool == True:
                correct_num += 1
                break
    #全ての述語が正しければ、"yes"を返す
    if correct_num == len_word:
        return "yes"
    else:
        return "no"

#check_kaku_frameを、京大格フレームの頻度を考慮するようにしたもの
@timeout_decorator.timeout(300)
def check_kaku_frame2(root, word_li, kaku_li, syugo_li):
    len_word = len(word_li)
    correct_num = 0
    for word, kaku, syugo in zip(word_li, kaku_li, syugo_li):
        bool = False
        for i, child in enumerate(root):
            head_word = child.attrib["headword"]
            heads = head_word.split('/')
            if word in heads:    
                for child2 in child:
                    for child3 in child2:
                        for child4 in child3:
                            #追加部分
                            if int(child4.attrib["frequency"]) < 2:
                                continue
                        this_kaku = child3.attrib["case"]
                        components = child3.findall("component")
                        for component in components:
                            comp = component.text.split('/')[0]
                            kaku2 = kaku + "格"
                            if comp == syugo and kaku2 == this_kaku:
                                bool = True
            if bool == True:
                correct_num += 1
                break
        if bool == False:
            break
    if correct_num == len_word:
        return "yes"
    else:
        return "no"


