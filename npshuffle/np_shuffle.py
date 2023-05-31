#普通の形態素解析では分割されてしまう名詞も１つの名詞として出す。
from pyknp import KNP, Juman
import timeout_decorator


#名詞の抽出
#@timeout_decorator.timeout(20)
def noun_extract(text, jumanpp):
    #jumanpp = Juman()
    #入力テキストを形態素解析
    result = jumanpp.analysis(text)
    noun_li = []
    hinshi_li = []
    noun = ""
    hinshi = ""
    #接頭辞・接尾辞・サ変名詞などを考慮して名詞を抽出
    for mrph in result.mrph_list():
        if mrph.hinsi == "名詞" or mrph.hinsi == "接頭辞":
            noun = noun + mrph.midasi
            if not "変" in hinshi:
                if not hinshi == "普通名詞":
                    hinshi = mrph.bunrui
        elif mrph.hinsi == "接尾辞":
            noun = noun + mrph.midasi
            if not "変" in hinshi:
                if not hinshi == "普通名詞":
                    hinshi = mrph.bunrui
        elif noun != "":
            noun_li.append(noun)
            noun = ""
            hinshi_li.append(hinshi)
            hinshi = ""
    return noun_li, hinshi_li

#名詞の入れ替え
def noun_shuffle(text, noun_li, hinshi_li):
    bool = False
    change_element = []
    for i, hinshi in enumerate(hinshi_li):
        tmp = hinshi_li[i+1:]
        tmp_num = i+1
        for hinshi2 in tmp:
            if hinshi == hinshi2 and "変" not in hinshi:
                word1 = noun_li[i]
                word2 = noun_li[tmp_num]
                word_len = len(word1)
                word_len2 = len(word2)
                pos = text.find(word1)
                pos2 = text.find(word2)
                word_pos = pos + word_len
                word_pos2 = pos2 + word_len2
                #助詞のと、やを介して隣り合っている名詞は入れ替えない
                if abs(word_pos - pos2) == 1 and (text[pos2-1] == "と" or text[pos2-1] == "や" or text[pos2-1] == "・" or text[pos2-1] == "、" or text[pos2-1] == ","):
                    continue
                #入れ替える名詞を配列に格納
                else:
                    change_element.append(word1)
                    change_element.append(word2)
                    bool = True
                break
            else:
                tmp_num += 1
        #入れ替える名詞が見つかったらループを抜ける
        if bool == True:
            break
    
    #入れ替える名詞が見つからなかったらNoneを返す
    if change_element == []:
        return None
    #入れ替える名詞をchange_partに置き換える
    for i, element in enumerate(change_element):
        if i == 0:
            text = text.replace(element, "first_change_part")
        if i == 1:
            text = text.replace(element, "second_change_part")
    #change_partを入れ替える名詞に置き換える
    for i in range(len(change_element)):
        if i == 0:
            text = text.replace("first_change_part", change_element[1])
        elif i == 1:
            text = text.replace("second_change_part", change_element[0])
    
    return text
