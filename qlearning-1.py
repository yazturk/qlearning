#!/usr/bin/python

import tkinter as tk
import numpy as np
import random
import matplotlib.pyplot as plt

#sabitler
en,boy = 30,30
kare = 13 #pixel
engel_r="#800" #koyu kırmızı
baslangic_r="blue"
hedef_r="green"
canvas_r="white" 

hedef_odulu = 50
engel_odulu = -5
bos_odulu = 3
learning_rate=0.9

class Nokta:
    def sec(self,i,j):
        self.i = i
        self.j = j
        print(i,j)

#global değişkenler
baslangic = Nokta()
hedef = Nokta()

#R ve Q matrislerinde ikinci indeksin anlamı
#Şu numaralara göre ilgili komşuya geçişi belirtir
# 0  1  2
# 3  N  4
# 5  6  7

R = np.empty(shape=(en*boy, 8), dtype=np.int8)
Q = np.zeros(shape=(en*boy, 8), dtype=np.float)
G = np.zeros(shape=(en*boy, 8), dtype=np.int) #geçildi bilgisi

episode_n = 0 

epsilon = 0
def rastgele():
    r = random.randint(0,200000)
    return r>epsilon

def main():
    global pencere,canvas,label,button,entry
    pencere=tk.Tk()
    pencere.geometry("700x700") #genişliğe uymayabilir

    canvas=tk.Canvas(pencere,bg=canvas_r, height=boy*kare+2,
        highlightcolor="yellow", width=en*kare+2)

    label = tk.Label(text="Engel yüzdesini girin:")
    label.pack()

    entry=tk.Entry()
    entry.pack()
    entry.insert(0,"30")

    button=tk.Button(text="Tamam",command=engel_doldur)
    button.pack()
    pencere.mainloop()


def kare_ciz(i,j,renk):
    y = i*kare+1
    x = j*kare+1
    canvas.create_rectangle(x, y, x+kare-2, y+kare-2, fill=renk)
    
def mouse_idle(e):
    pass

def bos_mu(i,j):
    if i==0:
        return R[(i+1)*en + j][1] == bos_odulu
    else:
        return R[(i-1)*en + j][6] == bos_odulu

def baslangic_sec(e):
    j = int(e.x/kare)
    i = int(e.y/kare)
    if bos_mu(i,j):
        baslangic.sec(i,j)
        kare_ciz(i,j, baslangic_r)
        canvas.bind("<Button-1>", hedef_sec)
        label['text']='Hedef noktası seçin'

def hedef_sec(e):
    j = int(e.x/kare)
    i = int(e.y/kare)
    if bos_mu(i,j):
        hedef.sec(i,j)
        etrafini_doldur(i,j,hedef_odulu)
        kare_ciz(i,j, hedef_r)
        canvas.bind("<Button-1>", mouse_idle)
        label['text']='Hedef seçildi'
        pencere.update_idletasks()
        #işletimi q_learning fonksiyonuna devret 
        q_learning()

def etrafini_doldur(i,j,puan):
    #else'ler kordinatın kendisini -128 ile doldurur,
    #-128 sınır dışı demektir
    #if'ler komşuları verilen puanla doldurur
    if i>0:
        R[(i-1)*en + j  ][6] = puan
    else:
        R[i*en + j][1] = -128
    if i>0 and j>0:
        R[(i-1)*en + j-1][7] = puan
    else:
        R[i*en + j][0] = -128
    if i>0 and j<en-1:
        R[(i-1)*en + j+1][5] = puan
    else:
        R[i*en + j][2] = -128
    
    if i<boy-1:
        R[(i+1)*en +j   ][1] = puan
    else:
        R[i*en + j][6] = -128

    if i<boy-1 and j>0:
            R[(i+1)*en + j-1][2] = puan
    else:
        R[i*en + j][5] = -128
    if i<boy-1 and j<en-1:
        R[(i+1)*en + j+1][0] = puan
    else:
        R[i*en + j][7] = -128
    if j>0:
        R[i*en + j-1][4] = puan
    else:
        R[i*en + j][3] = -128
    if j<en-1:
        R[i*en + j+1][3] = puan
    else:
        R[i*en + j][4] = -128

def engel_doldur():
    yuzde= int(entry.get())
    f = open("engel.txt","w")
    for i in range(0,boy):
        for j in range(0,en):
            r = random.randint(1,100)
            f.write("("+str(i)+", "+str(j)+", ")
            if r<yuzde:
                kare_ciz(i, j, engel_r)
                etrafini_doldur(i,j,engel_odulu)
                f.write("K)\n")
            else:
                etrafini_doldur(i,j,bos_odulu)
                f.write("B)\n")
    f.close()
    button.destroy()
    entry.destroy()
    #mouse'a yeni callback fonksiyonu atanır
    canvas.bind("<Button-1>", baslangic_sec)
    canvas.pack()
    label['text']='Başlangıç noktası seçin'
    print(R)

def q_learning():
    global hedef_durum, episode_n
    hedef_durum = hedef.i * en + hedef.j
    sonlan = 0 #ödül/adım oranı ardarda 5 defa 2.7'dan büyük gelirse sonlanacak
    adimlar=[]
    oranlar=[]
    #Daha belirli süre sürmesi için ikinci while döngüsü tercih edilebilir
    #while sonlan<5:
    while episode_n < 200:
        step_n, odul = episode()
        oran = odul/step_n
        if oran >= 2.7:
            sonlan += 1
        else:
            sonlan = 0
        print("Episode: ", episode_n, "\tAdım: ",step_n, "\tÖdül: ", odul, "\tOran: ", oran)
        episode_n+=1
        adimlar.append(step_n)
        oranlar.append(oran)

    epizodlar = range(0, episode_n)
    
    plt.figure()
    plt.plot(epizodlar, adimlar)
    plt.xlabel("Epizodlar")
    plt.ylabel("Adım sayısı")
    plt.show(block=False)

    plt.figure()
    plt.plot(epizodlar, oranlar)
    plt.xlabel("Epizodlar")
    plt.ylabel("Ödül / Adım Sayısı")
    plt.show(block=False)
    
    rota_ciz()

def episode():
    odul=0
    step_n=1
    durum = baslangic.i*en + baslangic.j
    while durum != hedef_durum:
        durum, yeniodul=step(durum)
        odul += yeniodul
        step_n += 1
    for d in G:
        for e in range(0,8):
            d[e] = 0 #geçildi değerlerini sıfırla
    return step_n, odul

def step(durum):
    global epsilon
    if rastgele():
        reward = -128
        while reward <= -128:
            eylem = random.randrange(0,8)
            reward = R[durum][eylem]
    else:
        eylem = en_uygun(durum)
        reward = R[durum][eylem]
        
    G[durum][eylem]+= 1
    if G[durum][eylem] > 100:
        print(durum)
        exit()

    yenidurum = next(durum,eylem)
    a, maks = maximum(yenidurum)
    Q[durum][eylem] = R[durum][eylem] + learning_rate * maks   
    
    epsilon += 1
    return yenidurum, reward


def en_uygun(durum): 
    #öncelikle, daha önce en az geçilmişler bulunur
    eylemler = []
    gecildi = 100000
    for e in range(0,8):
        if R[durum][e] != -128:
            yenidurum = next(durum, e)
            if G[durum][e] == gecildi:
                eylemler.append(e)
            elif G[durum][e] < gecildi:
                gecildi = G[durum][e]
                eylemler=[e]
    #sonra bunların içinden en uygunlar seçilir
    maks = -128
    eylem = -1
    eylemler2=[]
    for e in eylemler:
        if Q[durum][e] == maks:
            eylemler2.append(e)
        elif Q[durum][e] > maks:
            maks = Q[durum][e]
            eylemler2 = [e]
            
    #hala 1'den fazla aday varsa rastgele seçim yapılır   
    length = len(eylemler2)
    if length == 0:
        print("Hiçbir eylem seçilmedi")
        exit()    
    return eylemler2[random.randrange(0,length)]

def maximum(durum):
    maks = -128
    eylem = -1
    for e in range(0,8):
        if Q[durum][e] > maks:
            maks = Q[durum][e]
            eylem = e
    return eylem,maks

def next(durum,eylem):
    if eylem == 0:
        return (durum-en) - 1
    if eylem == 1:
        return durum-en
    if eylem == 2:
        return (durum-en)+1
    if eylem == 3:
        return durum-1
    if eylem == 4:
        return durum+1
    if eylem == 5:
        return durum+en-1
    if eylem == 6:
        return durum+en
    else:
        return durum+en+1

def rota_ciz():
    adim, odul = 0,0
    i,j = baslangic.i, baslangic.j
    durum = i*en+j
    while i != hedef.i or j != hedef.j:
        eylem = en_uygun(durum)
        adim += 1
        odul += R[durum][eylem]
        G[durum][eylem] += 1

        yenidurum = next(durum,eylem)
        i = yenidurum//en
        j = yenidurum%en
        if R[durum][eylem] == engel_odulu:
            kare_ciz(i,j,"red")
        else:
            kare_ciz(i,j,"gray")
        durum = yenidurum
        
    kare_ciz(baslangic.i, baslangic.j, baslangic_r)
    kare_ciz(i,j,hedef_r)
    label["text"] = "Adım sayısı %i, toplam ödül %i" % (adim,odul)
main()
