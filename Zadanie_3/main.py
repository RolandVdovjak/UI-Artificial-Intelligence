import numpy
import numpy as np
import random
import time
import copy

x = y = 0       # Rozmery zahrady
skaly = 0       # Pocet skal
zahrada = np.zeros(shape=(x,y))     # Pociatocna zahrada
Htable = {}     # Hash tabulka s originalnymi chromozomami
Population = [[]]   # Vsetky generacie v Populacii
last_move = ''  # Posledny krok
firstgen = []   # Prva generacia
Htable_garden = {}

# Trieda mnicha
class Monk:
    def __init__(self, chromosome, fitness, garden = None):
        self.chromosome = chromosome        # Chromozom
        self.fitness = fitness          # Fitnes
        self.garden = garden        # Zahrada

    # Pri sortovani sa sortuje podla fitnes
    def __lt__(self, other):
        return self.fitness < other.fitness

the_Monk = Monk('', 0)      # Vitazny mnich- ten ktory dokazal dokoncit

# Nahodne rozmiestni skaly po zahrade, skala == -1, vypis vypisuje -1 sivo
def rocks():
    global zahrada, skaly

    for i in range(skaly):
        sx = random.randint(2,x)
        sy = random.randint(2,y)
        zahrada[sy][sx] = -1

# Rozmiestnenie skal podla zadania
def default_rocks():
    global zahrada
    if x == 12 and y == 10:
        zahrada[3][2] = -1
        zahrada[5][3] = -1
        zahrada[4][5] = -1
        zahrada[2][6] = -1
        zahrada[7][9] = -1
        zahrada[7][10] = -1


# Urobi hranicu okolo zahrady s cislom -2, toto cislo vypis vypise zlto
def make_border():
    global zahrada

    zahrada[0] = -2
    zahrada[y+1] = -2

    for i in range(1, y+1):
        zahrada[i][0] = -2
        zahrada[i][x+1] = -2

# Parameter - 2D pole o x*y rozmeroch, Farebne vypisuje toto 2D pole
def print_garden(zahrada):

    for i in range(y+2):
        for j in range(x+2):
            # Skaly
            if zahrada[i][j] == -1.0:
                print("\033[47m    \033[00m", end="")
            # Hranica zahrady
            elif zahrada[i][j] == -2.0:
                print("\033[43m    \033[00m", end="")
            # Pohrabane policka
            elif zahrada[i][j] != 0.0:
                print("\033[92m{}\033[00m".format(str(zahrada[i][j])[:-2].rjust(3, ' ')), end=" ")
            # Nepohrabane policka
            else:
                print(str(zahrada[i][j])[:-2].rjust(3, ' '), end=" ")
        print()
    print()

# Vytvorenie povodnej geenracie
def make_first_gen(n):
    global x, y, skaly, Htable
    Population.append([])
    ch_size = x + y + 1

    i = 0
    # Dokym sa nenajde n roznych jedincov
    while i < n:
        new_ch = np.full(ch_size, 0)

        # Pohyby su v intervale -(x+y) po x+y
        for j in range(1, ch_size):     # 'j' je cislo riadku/ stlpca, ktore sa da na rnd poziciu v poli
            rnd = random.randint(0,x+y)
            direction = random.randint(0,1)

            # Smer pohybu
            if direction == 0:
                direction = -1

            # Ak rnd pozicia je volna, priradi sa, ak nie, tak na prvu volnu
            if new_ch[rnd] == 0:
                new_ch[rnd] = j*direction
            else:
                first_zero = np.where(new_ch==0)
                new_ch[int(first_zero[0][0])] = int(j)

        # Kontrola originality chromozomu
        if Htable.get(str(new_ch)):
            continue

        # Pridanie, vytvorenie, ...
        Htable[str(new_ch)] = True
        monk = Monk(new_ch, 0)
        Population[0].append(monk)
        i +=1

# Ked nasiel prekazku a zistil, ze sa da hybat, urci mozny smer pohybu
def obsticle(monk, garden, pos):
    global last_move
    decide = monk[len(monk)-1]

    options = []

    if garden[pos[1]+1][pos[0]] == 0:
        options.append('d')

    if garden[pos[1]-1][pos[0]] == 0:
        options.append('u')

    if garden[pos[1]][pos[0]+1] == 0:
        options.append('r')

    if garden[pos[1]][pos[0]-1] == 0:
        options.append('l')

    last_move = options[decide % len(options)] # podla posledneho genu urcuje pohyb ak je na vyber

# Zistovanie, ci je mnich zaseknuty
def stuck(pos, garden):
    global last_move

    # Ak je pozicia ina od okraja zahrady
    if garden[pos[1]][pos[0]] != -2:
        # Posledny pohyb dava do suvisu s moznou zmenou cesty, ak nenajde cestu, oznaci sa za zaseknuteho a vrati hodnotu True
        if last_move == 'd' and (garden[pos[1]][pos[0]+1] != -2 and garden[pos[1]][pos[0]-1] != -2):
            if garden[pos[1]+1][pos[0]] != 0 and garden[pos[1]][pos[0]+1] != 0 and garden[pos[1]][pos[0]-1] != 0:
                last_move = 's'
                return True

        elif last_move == 'u' and (garden[pos[1]][pos[0]+1] != -2 and garden[pos[1]][pos[0]-1] != -2):
            if garden[pos[1]-1][pos[0]] != 0 and garden[pos[1]][pos[0]+1] != 0 and garden[pos[1]][pos[0]-1] != 0:
                last_move = 's'
                return True

        elif last_move == 'l' and (garden[pos[1]+1][pos[0]] != -2 and garden[pos[1]-1][pos[0]] != -2):
            if garden[pos[1]][pos[0]-1] != 0 and garden[pos[1]+1][pos[0]] != 0 and garden[pos[1]-1][pos[0]] != 0:
                last_move = 's'
                return True

        elif last_move == 'r' and (garden[pos[1]+1][pos[0]] != -2 and garden[pos[1]-1][pos[0]] != -2):
            if garden[pos[1]][pos[0]+1] != 0 and garden[pos[1]+1][pos[0]] != 0 and garden[pos[1]-1][pos[0]] != 0:
                last_move = 's'
                return True
        elif garden[pos[1]][pos[0]+1] != -2 or garden[pos[1]][pos[0]-1] or garden[pos[1]+1][pos[0]] != -2 or garden[pos[1]-1][pos[0]] != -2:
            return True

    elif garden[pos[1]][pos[0]] == -2:
        return True
    else:
        return False

# Pohyb po zahrade
def move(garden, pos, move_num, monk):
    global last_move

    # Hybe sa podla posledneho pohybu
    if last_move == 'd':
        if garden[pos[1]+1][pos[0]] == -2:  # Hybe sa pokym sa nedostane na okraj zahrady resp ohradu
            return False
        if garden[pos[1]+1][pos[0]] == 0:   # Ak je volna cesta, pohne sa
            garden[pos[1]+1][pos[0]] = move_num
            pos[1] += 1
        else:
            if stuck(pos, garden):      # Ked nie je volna cesta, zistuje, ci je zaseknuty
                return False
            obsticle(monk, garden, pos)     # Ak nie je zaseknuty, zistuje smer, ktorym pojde

    elif last_move == 'u':
        if garden[pos[1]-1][pos[0]] == -2:
            return False
        if garden[pos[1]-1][pos[0]] == 0:
            garden[pos[1]-1][pos[0]] = move_num
            pos[1] -= 1
        else:
            if stuck(pos, garden):
                return False
            obsticle(monk, garden, pos)

    elif last_move == 'l':
        if garden[pos[1]][pos[0]-1] == -2:
            return False
        if garden[pos[1]][pos[0]-1] == 0:
            garden[pos[1]][pos[0]-1] = move_num
            pos[0] -= 1
        else:
            if stuck(pos, garden):
                return False
            obsticle(monk, garden, pos)

    elif last_move == 'r':
        if garden[pos[1]][pos[0]+1] == -2:
            return False
        if garden[pos[1]][pos[0]+1] == 0:
            garden[pos[1]][pos[0]+1] = move_num
            pos[0] += 1
        else:
            if stuck(pos, garden):
                return False
            obsticle(monk, garden, pos)

    else:
        return False

    return True

# Funkcia vytvara fitnes hodnotu danemu chromozomu, pocas vyvarania aj hrabe
def fitness(Monk):
    global x, y, zahrada, last_move, the_Monk
    fit = 1     # fitnes
    monk = Monk.chromosome      # monk = chromozom vstupneho mnicha
    pos = [0, 0]            # pozicia vstupu do zahradky
    garden = copy.deepcopy(zahrada)     # zahradka daneho mnicha
    move_num = 0        # cislo pohybu

    # Hrabanie (prechod po kazdom gene)
    for i in range(len(monk)):
        move_num += 1

        # Zistenie vstupnej pozicie a urcenia smeru pohybu podla hodnoty genu
        if monk[i] >= 0:
            if monk[i] >= x+1:
                pos[0] = x + 1
                pos[1] = monk[i]-x
                last_move = 'l'
            else:
                pos[0] = monk[i]
                pos[1] = 0
                last_move = 'd'
        else:
            if monk[i] <= -x-1:
                pos[0] = 0
                pos[1] = (monk[i]+x) * -1
                last_move = 'r'
            else:
                pos[0] = monk[i] * -1
                pos[1] = y + 1
                last_move = 'u'

        # Hrabanie
        while True:
            if move(garden, pos, move_num, monk):   # Pohyb ako taky
                continue
            else:
                break

        # Kontrola zaseknutosti
        if last_move == 's':
            fit -= int(x*y/100*25)  # zmensenie fitnes
            fit += i
            break

        # Ak nasiel riesenie - konci cyklus
        if len(np.where(garden==0)[0]) == 0:
            the_Monk.chromosome = monk
            the_Monk.garden = garden
            the_Monk.fitness = 1
            break

    if len(np.where(garden==0)[0]) < 50:
        if Htable_garden.get(str(str(np.where(garden == 0)[0])[1:-1] + str(np.where(garden == 0)[1])[1:-1])) != None :
            Htable_garden[str(str(np.where(garden == 0)[0])[1:-1] + str(np.where(garden == 0)[1])[1:-1])] += 0.03
            fit -= Htable_garden.get(str(str(np.where(garden == 0)[0])[1:-1] + str(np.where(garden == 0)[1])[1:-1]))
        else:
            Htable_garden[str(str(np.where(garden == 0)[0])[1:-1] + str(np.where(garden == 0)[1])[1:-1])] = 0.03


    # Pripocitavanie / odpocitavanie fitnes
    fit += x*y*2 - len(np.where(garden==0)[0]) -i

    Monk.fitness = fit
    Monk.garden = garden

# Vyber elitizmom
def elitism(i):
    global Population
    Population[i] = Population[i][:16]  # Prvi 16ti

# Vyber turnajom
def tournament(i):
    global Population
    num_monks = len(Population[i])
    new_gen = []

    # Trikrat urobi populaciu polovicnou oproti zaciatku
    for k in range(3):
        new_gen.clear()

        # Turnaj o dvojicjiach mnichov zo zaciatku a z konca generacie
        for j in range(int(num_monks/pow(2, k+1))):
            if random.random() > 0.2:
                new_gen.append(Population[i][j])
            else:
                new_gen.append(Population[i][int(num_monks/pow(2, k+1))-j])

        Population[i] = new_gen[:]

# Krizenie
def cross(a, b):
    rnd = random.randint(1, len(a.chromosome)-1)
    new = np.append(a.chromosome[:rnd], b.chromosome[rnd:])

    # Nemuseli by sa vyskytovat 2 rovnake geny
    for i in range(rnd, len(new)-1):
        where = np.where(new == new[i])
        if len(where[0]) > 1:
            new[i] = new[i] * (-1)

    return new

# Mutovanie
def mutate(a):
    global Htable
    while Htable.get(str(a.chromosome)):
        rnd1 = random.randint(0, 2)
        c1 = a.chromosome[random.randint(0, len(a.chromosome) - 1)]
        c1pos = np.where(a.chromosome == c1)[0][0]

        c2 = random.randint(1,x+y-1)
        c2pos = np.where(a.chromosome == c2)

        if len(c2pos[0]) == 0:
            c2pos = c1pos
        else:
            c2pos = c2pos[0]

        if rnd1 == 2:
            c2 = random.randint(0,x+y-1)
            c2pos = c1pos
            mutate(a)

        if rnd1 == 1:
            c2 = random.randint(0,x+y-1) * (-1)
            c2pos = random.randint(0,x+y-1)

        if rnd1 == 0:
            a.chromosome[c1pos] = c1 * (-1)
            if a.chromosome[len(a.chromosome)-1] > x+y-1:
                a.chromosome[len(a.chromosome) - 1] = 0
            a.chromosome[len(a.chromosome)-1] +=1

    return a.chromosome

# Krizenie
def g_crossing(i):
    global Htable, Population
    Population.append([])
    l = n = 0

    # 112 mnichov je skrizenych
    while n < 112:
        # Skusa krizit kazdeho s kazdym pokial sa nedostane ku 112 novym
        for j in range(len(Population[i])):
            for k in range(len(Population[i]) - j - 1):

                # Dvojica ma dvoch potomkov
                new_monk1 = Monk(cross(Population[i][j], Population[i][j+k+1]), 0) # Krizenie
                new_monk2 = Monk(cross(Population[i][j+k+1], Population[i][j]), 0) # Krizenie
                l += 1

                # Ak sa dane chromozomy uz niekedy vytvorili, zmutuju
                if Htable.get(str(new_monk1.chromosome)) or Htable.get(str(new_monk2.chromosome)):
                    new_monk1 = Monk(mutate(new_monk1), 0)
                    new_monk2 = Monk(mutate(new_monk2), 0)

                # Ak este neexistuje dany chromozom, vytvori sa
                if Htable.get(str(new_monk1.chromosome)) != True:
                    Htable[str(new_monk1.chromosome)] = True
                    Population[i + 1].append(new_monk1)
                    n += 1
                elif Htable.get(str(new_monk2.chromosome)) != True:
                    Htable[str(new_monk2.chromosome)] = True
                    Population[i + 1].append(new_monk2)
                    n += 1

                if n == 112:
                    break
            if n == 112:
                break

    # 16 mnichov - prvi z novej generacie, ktory zmutovali
    for j in range(16):
        new_monk = Monk(mutate(Population[i+1][j]), 0)  # mutovanie
        Htable[str(new_monk.chromosome)] = True
        Population[i+1].append(new_monk)
        l += 1

# Geneticky algoritmus
def gen_algorithm(ch):
    f = open("out{}.txt".format(ch), 'w')

    # pociatocna generacia
    for i in range(128):
        fitness(Population[0][i])

    # Evolucia
    g = 0
    while the_Monk.fitness == 0 and g < 300:
        g = evolve(g, ch, f)

    get_best()
    print("Type: ", ch, "\nGenerations: ", g)
    if isinstance(last_move, int):
        print("Best Monk in generation: ", last_move)
    print_garden(the_Monk.garden)

    f.close()

# Evolvuj
def evolve(g, ch, f):

    # Fitnes danej populacie
    for i in range(128):
        fitness(Population[g][i])
    Population[g].sort(reverse=True)
    save(f, g)
    # Rozhodnutie pre typ vyberu
    if ch == 'e':
        elitism(g)
    else:
        tournament(g)

    # Vypis najlepsieho mnicha aj s poradim generacie
    #print(g, ch)
    #print_garden(Population[g][0].garden)
    g_crossing(g)
    g += 1
    return g

def save(f, g):

    f.write("{:.2f};".format(Population[g][0].fitness))
    f.write("{:.2f};".format((Population[g][63].fitness + Population[g][64].fitness)/2))
    f.write("{:.2f}\n".format(Population[g][127].fitness))

def get_best():
    global the_Monk, Population, last_move
    best = Population[0][0]
    if the_Monk.fitness == 0:
        for i in range(299):
            if Population[i][0].fitness > best.fitness:
                best = Population[i][0]
                last_move = i
        the_Monk = best


#----------------------------------_M_A_I_N_----------------------------------#

def main():
    random.seed(time.time())
    global zahrada, x, y, skaly, the_Monk, firstgen

    monk = np.array([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 0, 2, 3, 5, 1, 4])
    a = Monk(monk, 0)

    x =12 #int(input("Sirka:\t"))
    y =10 #int(input("Dlzka:\t"))

    skaly = int(x*y/100*5)
    zahrada = np.zeros(shape=(y+2,x+2))

    if x != 12 or y != 10:
        rocks()
    default_rocks()
    make_border()
    print_garden(zahrada)

    make_first_gen(128)
    firstgen = copy.deepcopy(Population[0])


    gen_algorithm('e')

    Population.clear()
    Population.append([])
    Htable_garden.clear()
    Htable.clear()
    Population[0] = copy.deepcopy(firstgen)
    the_Monk.fitness = 0

    gen_algorithm('t')



if __name__ == '__main__':
    main()