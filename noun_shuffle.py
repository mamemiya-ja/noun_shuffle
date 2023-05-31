import glob
import re
import csv
import xml.etree.ElementTree as ET 
import npshuffle
import MeCab
import ipadic
from pyknp import KNP, Juman


# XMLファイルを解析(京大格フレームコーパス)
tree = ET.parse('ファイル') 

# XMLを取得
root = tree.getroot()
print("xml取得")

wakati = MeCab.Tagger(ipadic.MECAB_ARGS)
jumanpp = Juman()

#wikiデータ抽出
l = glob.glob('ファイル')
c = 0
for file_num, file in enumerate(l):
    knp = KNP(option = '-tab -anaphora', jumanpp=False)
    #jumanpp = Juman()
    print("file_name", file)
    lines = []
    with open(file) as f:
        for line in f:    
            if line != "\n" and "doc" not in line:
                line2 = line.replace("\n", "")
                #41文字以上の文を削除
                if len(line2) < 41:
                    lines.append(line2)

    print("line_num", len(lines))

    #残った文章の名詞をランダムにシャッフルする。
    original_texts = []
    changed_texts = []
    e = 0
    for result in lines:
        #前処理：全角スペース、半角スペース、括弧内の文字を削除
        text = result
        text = text.replace("　", "")
        text = text.replace(" ", "")
        text = re.sub('（.+）', "", text)
        text = re.sub('\(.+\)', "", text)
        if 3 > len(text):
            continue
        
        #名詞とその品詞を抽出
        #jumanでタイムアウトエラーが出てしまう。
        try:
            noun_li, hinshi_li = npshuffle.np_shuffle.noun_extract(text, jumanpp)
        except:
            continue
        #名詞を入れ替えた文を作成
        changed_text = npshuffle.np_shuffle.noun_shuffle(text, noun_li, hinshi_li)
        if changed_text != None:
            original_texts.append(text)
            changed_texts.append(changed_text)
        
        e += 1
        if e % 50 == 0:
            jumanpp = Juman()

    print("シャッフル完了")
    print("changed_num", len(changed_texts))

    #シャッフルした文章を格フレームと照らし合わせて不自然な文章を削除
    remain_changed_text = []
    remain_original_text = []
    n = 0
    for line, origin in zip(changed_texts, original_texts):
        #前処理：全角スペース、半角スペース、括弧内の文字を削除
        text = line
        text = text.replace("　", "")
        text = text.replace(" ", "")
        text = re.sub('（.+）', "", text)
        text = re.sub('\(.+\)', "", text)
        #句点がない文を削除
        if "。" not in text:
            continue
        if len(text) < 41:
            #作成した文の格フレームを取得
            li = npshuffle.kaku_frame.analyze_pas(text, knp)
            #格フレームから主語・格・述語を抽出
            word_li, kaku_li, syugo_li = npshuffle.kaku_frame.kaku_extract(li)
            if word_li == [] or kaku_li == [] or syugo_li == []:
                continue
            #格フレームの主語・格・述語を、京大格フレームと照合
            result = npshuffle.kaku_frame.check_kaku_frame2(root, word_li, kaku_li, syugo_li)
            if result != "no":
                remain_changed_text.append(text)
                remain_original_text.append(origin)
        n += 1
        if n % 50 == 0:
            knp = KNP(option = '-tab -anaphora', jumanpp=False)

    print("チェック完了")
    print("checked_num", len(remain_changed_text))

    #格フレームチェックして残った文章をcsvに書き込む
    with open("ファイル", "a") as f2:
        writer = csv.writer(f2)
        for r_origin, r_changed in zip(remain_original_text, remain_changed_text):
            writer.writerow([r_origin, r_changed])



