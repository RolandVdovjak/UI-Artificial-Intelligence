import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time

data_set = {}
k = 15
counter = 0
size = 20 + 2000

# Bod - suradnice a farba
class POINT:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

# Klasifikacia bodu
def classify(point):
    global data_set, k, counter
    closest = [[0, 0, 0, 0], [0, 0, 0, 0], [100000, 100000, 100000, 100000]]
    c = ['red', 'green', 'blue', 'purple']
    original_color = point.color

    # Najdenie vsetkych vzdialenosti
    disatnces = [[np.sqrt((point.x-p.x)**2 + (point.y-p.y)**2), p.color]for p in data_set.values()]

    # Zoradenie vzdialenosti
    k_id = sorted(disatnces, key=lambda x:x[0])

    # Priradovanie poctu farbam ktore su blizke
    for i in range(k):
        if k_id[i][1] == 'red':
            id = 0
        elif k_id[i][1] == 'green':
            id = 1
        elif k_id[i][1] == 'blue':
            id = 2
        elif k_id[i][1] == 'purple':
            id = 3

        closest[0][id] += float(k_id[i][0])
        closest[1][id] += 1

    # Spocitanie priemernej vzdialenosti farieb
    for i in range(4):
        if closest[1][i] > 0:
            closest[2][i] = closest[0][i] / closest[1][i]

    # Rovnaky pocet blizkych bodov
    col = np.where(closest[1] == np.max(closest[1]))

    # Ak je viac rovnakych farieb v rovnakom pocte, vyberie tesn s priemerne blizsou vzdialenostou
    if len(col[0])>1:
        point.color = c[np.argmin(closest[2])]
    else:
        point.color = c[np.argmax(closest[1])]

    # Pocitanie presnosti
    if original_color != point.color:
        counter += 1

# Vkladanie bodu
def set_point(color):
    global data_set

    # Urcenie hranic pre priradovanie random cisel
    if random.randint(1, 100) < 100:
        if color == 'red':
            boundries_x = [-5000, 500]
            boundries_y = [-5000, 500]
        elif color == 'green':
            boundries_x = [-500, 5000]
            boundries_y = [-5000, 500]
        elif color == 'blue':
            boundries_x = [-5000, 500]
            boundries_y = [-500, 5000]
        elif color == 'purple':
            boundries_x = [-500, 5000]
            boundries_y = [-500, 5000]
    else:
        boundries_x = [-5000, 5000]
        boundries_y = [-5000, 5000]

    # Najdenie random cisla
    while True:
        x = random.randint(boundries_x[0], boundries_x[1])
        y = random.randint(boundries_y[0], boundries_y[1])
        key = (x, y)

        # Ak naslo random cislo
        if key not in data_set:

            point = POINT(x, y, color)  # Vytvori bod
            classify(point)         # Klasifikuje
            data_set[key] = point   # Priradi do dir
            return data_set[key]

# Make
def make(graph_num, k1, R, G, B, P):
    global data_set, counter, k

    # Nastavenie premennych pred spustenim tvorenia bodov
    k = k1
    random.seed(10005)
    start = time.time()
    data_set = {}
    counter = 0
    for i in range(5):              # Pociatocne body
        key_r = (R[0][i], R[1][i])
        key_g = (G[0][i], G[1][i])
        key_b = (B[0][i], B[1][i])
        key_p = (P[0][i], P[1][i])

        data_set[key_r] = POINT(R[0][i], R[1][i], 'red')
        data_set[key_g] = POINT(G[0][i], G[1][i], 'green')
        data_set[key_b] = POINT(B[0][i], B[1][i], 'blue')
        data_set[key_p] = POINT(P[0][i], P[1][i], 'purple')

    # Vytvaranie bodov
    for i in range(size-20):
        color_id = i % 4

        if color_id == 0:
            color = 'red'
        elif color_id == 1:
            color = 'green'
        elif color_id == 2:
            color = 'blue'
        elif color_id == 3:
            color = 'purple'

        point = set_point(color)

    # Efektivne vlozenie do grafu
    data = list(data_set.values())
    x_arr = []
    y_arr = []
    color_arr = []
    for val in data:        # Naplnenie suradnic
        x_arr.append(val.x)
        y_arr.append(val.y)
        color_arr.append(val.color)

    end = time.time()
    p = (size-counter)/size*100
    print("{:.2f}".format(p))
    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)

    plt.subplot(2,2,graph_num)
    plt.title("K= {}".format(k))
    plt.xlabel("T = {:.2f}s P = {:.2f}%".format(end-start, p))

    plt.scatter(x=x_arr, y=y_arr, color=color_arr, s=22)
    # plt.savefig('graph/graph3_'+str(k)+'.png')

# ____________________________M_A_I_N____________________________ #
def main():
    global data_set

    # Pociatocne body
    R = [[-4500, -4100, -1800, -2500, -2000], [-4400, -3000, -2400, -3400, -1400]]
    G = [[4500, 4100, 1800, 2500, 2000], [-4400, -3000, -2400, -3400, -1400]]
    B = [[-4500, -4100, -1800, -2500, -2000], [4400, 3000, 2400, 3400, 1400]]
    P = [[4500, 4100, 1800, 2500, 2000], [4400, 3000, 2400, 3400, 1400]]

    # Volanie funkcie make, k je druhy parameter

    # for i in range(1, 21):
    #     make(1,i,R,G, B, P)

    make(1,1,R,G, B, P)
    make(2,3,R,G, B, P)
    # make(1,5,R,G, B, P)
    make(3,7,R,G, B, P)
    # make(1,9,R,G, B, P)
    # make(1,11,R,G, B, P)
    # make(1,13,R,G, B, P)
    make(4,15,R,G, B, P)
    # make(1,17,R,G, B, P)
    # make(1,19,R,G, B, P)

    # Graf
    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)
    plt.tight_layout(pad=0.5)
    plt.show()


if __name__ == '__main__':
    main()