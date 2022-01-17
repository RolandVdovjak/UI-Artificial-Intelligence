import numpy as np
import copy
import heapq
import time

m = n = 0       # m je os X, n je os Y
nodecnt = allnodecnt = 0        # Pocitadla uzlov

    # VSTUP
s_matrix = np.array([[5,3,4], [1,2,0]])

e_matrix = np.array([[0,1,2], [3,4,5]])

    # UZOL
class NODE:
    def __init__(self, matrix, H, G, A, space, parent, operation):
        self.matrix = matrix            # stav reprezentovany maticou
        self.H = H                  # Heuristika
        self.G = G                  # Vzdialenost
        self.A = A                  # Kombinacia heuristiky a vzdialenosti
        self.space = space              # Medzera v hlavolame
        self.parent = parent            # Predchadzajuci stav
        self.operation = operation          # Posledne pouzity operator

        # Heapq funkcia push pridava do heapq podla porovnania velkosti, tato cast zabezpecuje porovnanie
    def __lt__(self, other):
        if self.A == other.A:
            return self.H < other.H
        else:
            return self.A < other.A

    # HEURTISTIKA 1- pocet cisel, ktore nie su na svojom mieste
def heuristic_1(matrix):
    h = 0
    for i in range(n):
        for j in range(m):
            if matrix[i][j] == 0:
                continue
            if matrix[i][j] != e_matrix[i][j]:
                h += 1

    return h

    # HEURTISTIKA 2- sucet vzdialenosti jednotlivych policok od cielovej pozicie
def heuristic_2(matrix):
    h = l = k = 0
    for i in range(n):
        for j in range(m):
            if matrix[i][j] == 0:
                continue
            position = np.argwhere(e_matrix == matrix[i][j])
            x = int(str(position)[2])
            y = int(str(position)[4])

            h += abs(x-i) + abs(y-j)

    return h

    # Zistenie rozmeru vstupnej matice
def get_mn():
    global matica, m, n
    m = len(s_matrix[0])    # os X
    n = len(s_matrix)       # os Y

    # Vypsi matice do konzoly
def print_matrix(matrix):
    for i in range(n):
        print("\t", end = "")
        for j in range(m):
            print(matrix[i][j], " ", end="")
        print()
    print()

def check_move(input):
    num = 0

    #UP
    if input.space[0] != str(n - 1):
        num += 1
    #DOWN
    if input.space[0] != '0':
        num += 10
    #LEFT
    if input.space[2] != str(m - 1):
        num += 100
    #RIGHT
    if input.space[2] != '0':
        num += 1000

    num -= input.operation      # Odcitanie predchadzajucej operacie

    return str(num).rjust(4,"0")[::-1]      # Vratia otoceny string doplneny o pripadne volne miesta

    # POHYB DOLE (Analogicky su riesene aj ostatne pohyby)
def m1(input):
    matrix = copy.deepcopy(input)

        # Pozicia medzery
    x = int(matrix.space[2])
    y = int(matrix.space[0])

        # Vymena cisiel
    matrix.matrix[y][x] = matrix.matrix[y + 1][x]
    matrix.matrix[y + 1][x] = 0

        # Upravenie uzla
    matrix.G = input.G +1
    matrix.space = "{} {}".format(y+1,x)
    matrix.parent = input
    matrix.operation = 10

    return matrix   # Vracia upraveny posunuty uzol

    # POHYB HORE
def m10(input):
    matrix = copy.deepcopy(input)
    x = int(matrix.space[2])
    y = int(matrix.space[0])
    matrix.matrix[y][x] = matrix.matrix[y - 1][x]
    matrix.matrix[y - 1][x] = 0

    matrix.G = input.G +1
    matrix.space = "{} {}".format(y - 1, x)
    matrix.parent = input
    matrix.operation = 1

    return matrix

    # POHYB DORPAVA
def m100(input):
    matrix = copy.deepcopy(input)
    x = int(matrix.space[2])
    y = int(matrix.space[0])
    matrix.matrix[y][x] = matrix.matrix[y][x + 1]
    matrix.matrix[y][x + 1] = 0

    matrix.G = input.G +1
    matrix.space = "{} {}".format(y, x + 1)
    matrix.parent = input
    matrix.operation = 1000

    return matrix

    # POHYB DOLAVA
def m1000(input):
    matrix = copy.deepcopy(input)
    x = int(matrix.space[2])
    y = int(matrix.space[0])
    matrix.matrix[y][x] = matrix.matrix[y][x - 1]
    matrix.matrix[y][x - 1] = 0

    matrix.G = input.G +1
    matrix.space = "{} {}".format(y, x - 1)
    matrix.parent = input
    matrix.operation = 100

    return matrix

    # A* ALGORITMUS
def a_star(start, h_type):
        # pocitadla spracovanych a vsetkych uzlov
    global nodecnt, allnodecnt
    nodecnt = allnodecnt = 0

    Htable = {} # Hash tabulka s uz vytvorenymi uzlami
    heap = []   # Heapq radena podla minima hodnoty A v uzle
    q = []      # Pole na ukladanie uzlov pre push-om do heapq

    root = copy.deepcopy(start)     # Nastavi root na pociatocny uzol
    heapq.heappush(heap, root)      # Prida do heapq

        # Cyklus hladania riesenia sa opakuje, kym nenajde riesenie alebo je hlbka vacsia ako 37
    while root.H != 0 and root.G < 37:
        current = copy.deepcopy(root)
        move_options = check_move(current)

            # Pre kazdy zo 4 moznych pohybov
        for i in range(4):
            if move_options[i] == '1':
                current = eval("m" + str(10**i) + '(current)')  # Pohyb
                allnodecnt += 1
                if Htable.get(str(current.matrix)) is None:     # Kontrola stavu pri uz vytvorenych stavoch
                    Htable[str(current.matrix)] = True
                    current.H = eval("heuristic_" + h_type + '(current.matrix)')
                    current.A = current.G + current.H
                    q.append(current)
                    current = current.parent

            # Vytvorene uzly prida do heapq
        for i in range(len(q)):
            heapq.heappush(heap, q[i])
        q.clear()

            # Nastavi root na najvhodnejsi prvok z heapq
        root = heapq.heappop(heap)

        nodecnt += 1

    return root     # Vracia uzol s riesenim, pomocou odkazovania na predchodcu vieme zistit cestu ku zaciatku

    # PRELOZENIE HODNOTY NA POHYB
def translate_move(move):
    if move == 10:
        return "Up"

    if move == 1:
        return "Down"

    if move == 1000:
        return "Left"

    if move == 100:
        return "Right"


#...............................................M.A.I.N.....................................................#
def main():
    path = []   # Pole s cestou od zaciatku po koniec

    get_mn()    # Zistenie rozmerov vstupnej matice

    global nodecnt, allnodecnt

    pos = str(np.argwhere(s_matrix == 0))[2:-2]     # Pozicia 0 na zaciatku hlavolamu

    start = NODE(s_matrix, heuristic_1(s_matrix), 0, heuristic_1(s_matrix), pos,  None, 0)      # Vytvaranie pociatocneho uzla

        #   HEURISTIKA 1
    t = 0
            # Pat opakovani
    for i in range(5):
        s = time.time()
        goal = a_star(start, "1")
        e = time.time()
        t += e-s

            # Zistenie vysledku
    if goal.H != 0:
        print("NO SOLUTION")
    else:
            # Pridanie cesty do pola
        while goal.parent != None:
            path.append(goal)
            goal = goal.parent
            i += 1

        print("\nHEURISTIC 1\n\tINPUT:")
        print_matrix(s_matrix)

            # Vypis cesty
        for i in range (len(path)):
            print("STEP: {}\nMove: {}".format(i+1, translate_move(path[len(path)-1-i].operation)))
            print_matrix(path[len(path)-1-i].matrix)

            # Vypis udajov o rieseni
        print("Time: {:.3f}".format(t/5) , "\nCreated nodes:", nodecnt, "\nProcessed nodes:", allnodecnt)

    i = 0
    path.clear()

        #   HEURISTIKA 2
    t = 0
           # Pat opakovani
    for i in range(5):
        s = time.time()
        goal = a_star(start, "2")
        e = time.time()
        t += e-s

        # Zistenie vysledku
    if goal.H != 0:
        print("NO SOLUTION")
    else:
            # Pridanie cesty do pola
        while goal.parent != None:
            path.append(goal)
            goal = goal.parent
            i += 1
        print("\nHEURISTIC 2\n\tINPUT:")
        print_matrix(s_matrix)

            # Vypis cesty
        for i in range (len(path)):
            print("STEP: {}\nMove: {}".format(i+1, translate_move(path[len(path)-1-i].operation)))
            print_matrix(path[len(path)-1-i].matrix)

            # Vypis udajov o rieseni
        print("Time: {:.3f}".format(t/5) , "\nCreated nodes:", nodecnt, "\nProcessed nodes:", allnodecnt)

if __name__ == '__main__':
    main()