from contextlib import AbstractAsyncContextManager
from re import A, T
import matplotlib.pyplot as plt
import numpy as np
from point import Point
from typing import Callable, List
import sympy as sp
from sympy.solvers.solveset import solvify
from copy import *


class Complex():
    def __init__(self):
        self.points = []
        self.pointsCount = 0
        self.xCount = 0
        self.epsilon = 0
        self.stop = False

    # Ustawia wartości do zmiennych Complexu
    def set(self, new_points):
        self.points = new_points
        self.pointsCount = len(new_points)
        # self.xCount = len(new_points[0])

    def fill(self, cubeConstraints, constraintsFuns, objFunction, epsilon):
        # wartosc do warunku stopu
        self.epsilon = epsilon

        # liczba wspolrzednych, zaklada sie, ze kazda wsp. ma ograniczenia
        self.xCount = int(len(cubeConstraints))

        # liczba punktow
        points = self.xCount + 2

        for point_it in range(0, points):

            # print("=====================================")
            # print("Punkt", point_it)
            # tablica na wspolrzedne o dlugosci liczby wspolrzednych (x0, x1, x2...)
            x = [None] * self.xCount

            # liczba funkcji ograniczen
            functions = int(len(constraintsFuns))

            # przygotowanie list
            result = [None] * functions

            # losowanie wspolrzednych pierwszego punktu
            for it in range(0, self.xCount):

                # poczatek zakresu losowania
                l = cubeConstraints[it][0]

                # koniec zakresu losowania
                u = cubeConstraints[it][1]

                # pierwszy punkt jest losowany w pelnym zakresie
                if point_it == 0:
                    x[it] = np.random.uniform(l, u)

                # kazdy kolejny punkt zgodnie ze wzorem (311)
                else:
                    r = np.random.uniform(0, 1)
                    x[it] = u + r * abs(u - l)

            tmp_point = Point(x, point_it)

            self.addPoint(tmp_point, constraintsFuns,
                          cubeConstraints, objFunction, c_fun="centrum")

    # Dodaje podany punkt do complexu. Sprawdza, czy znajduje sie w obszarze dopuszczalnym, jezeli nie, to go poprawia

    def addPoint(self, point, constraintsFuns, cubeConstraints, objFunction, c_fun):

        point = self.correctPoint(
            point, constraintsFuns, cubeConstraints, objFunction, c_fun)
        self.points.append(
            Point(point.get(), point.getID()))
        # point.display()
        self.pointsCount += 1

    # Sprawdza, czy podany punkt znajduje sie w obszarze dopuszczalnym,
    #   – jezeli nie, to go poprawia i zwraca
    #   – jezeli tak, to po prostu go zwraca bez zmian
    def correctPoint(self, point, constraintsFuns, cubeConstraints, objFunction, c_fun):
        # sprawdzenie, czy wylosowane wspolrzedne znajduja sie w obszarze ograniczonym funkcjami
        again = not(self.checkConstraints(
            point, constraintsFuns, cubeConstraints))
        debug_counter_1 = 0
        movesCounter = 0
        # print("Punkt przed poprawą: ", end='')
        # point.display()
        # print()
        while again:  # x_var_it <= self.x_variables:
            # debug_counter_1 += debug_counter_1
            # if debug_counter_1 >= 100:
            #     print("Tutaj coś nie gra")
            #     break
            # print("AGAIN: ", END='')
            # jezeli punkt nie spelnia ograniczen, to
            # w przypadku pierwszego punktu losowanie tego punktu jest powtarzane
            if point.getID() == 0 and again:
                # print("\npierwszy punkt, powtarzam, bo ", end='')
                # p = point.get().copy()
                # tabX.append(p[0])
                # tabY.append(p[1])

                # debug_counter_1 += 1
                # if debug_counter_1 >= 1000:
                #     print("PSUJE SIE PRZY PIERWSZYM PUNKCIE PO PROBACH",
                #           debug_counter_1)
                #     break

                new_x = []
                for it in range(0, self.xCount):
                    l = cubeConstraints[it][0]
                    u = cubeConstraints[it][1]
                    new_x.append(np.random.uniform(l, u))

                point.set(new_x)

            # jezeli punkt nie spelnia ograniczen, to
            # w przypadku kazdego innego punktu jest on przesuwany w strone centrum zaakceptowanych juz punktow o polowe odleglosci
            elif point.getID() != 0 and again:
                if c_fun == "centroid":

                    worst_point = self.getWorstPoint(objFunction)
                    centroid = self.centroid(worst_point)
                    self.moveHalfwayToCentroid(point, centroid)
                elif c_fun == "centrum":
                    self.moveHalfwayToCentrum(point)
                else:
                    "BŁĄD W KODZIE #1"

                # print("Jeżeli jest False, to punkt lezy w obszarze niedopuszczalnym:",
                #       self.checkConstraints(point, constraintsFuns, cubeConstraints))

                movesCounter += 1
                if movesCounter >= 10:

                    # print("Algorytm na razie stworzył", self.pointsCount,
                    #       "punktów.")

                    # print("Algorytm", movesCounter,
                    #       "razy poprawiał punkt przesuwając go do 'c'")
                    worst_point = self.getWorstPoint(objFunction)
                    c_p = self.centroid(worst_point)
                    # print("Jeżeli jest False, to 'c'' lezy w obszarze niedopuszczalnym:",
                    #       self.checkConstraints(c_p, constraintsFuns, cubeConstraints))

                    c = c_p.get()

                    point.set(c)

                    # print("Jeżeli jest False, to punkt lezy w obszarze niedopuszczalnym:",
                    #       self.checkConstraints(point, constraintsFuns, cubeConstraints))

                    break

            # Funkcja zwraca wartosci:
            #   – True, jezeli punkt spelnia warunki ograniczen
            #   – False, jezeli punkt nie spelnia chociaz jednej funkcji ograniczen
            again = not(self.checkConstraints(
                point, constraintsFuns, cubeConstraints))

        # print("Punkt został poprawiony i teraz, jeżeli jest False, to punkt lezy w obszarze niedopuszczalnym:",
        #       self.checkConstraints(point, constraintsFuns, cubeConstraints))
        # print()
        # circleX = np.linspace(-3, -1, 50)
        # print(circleX)
        # circleY1 = []
        # circleY2 = []
        # for x in circleX:
        #     circleY1.append(np.sqrt(1 - np.power(x+2, 2)))
        #     circleY2.append(-np.sqrt(1 - np.power(x+2, 2)))

        # # print(circleY1)
        # fig, ax = plt.subplots()
        # ax.scatter(tabX, tabY)
        # ax.plot(circleX, circleY1)
        # ax.plot(circleX, circleY2)
        # plt.show()

        # jezeli punkt spelnia ograniczenia, to program wychodzi z petli while i zwraca ten punkt
        return point

    def addPointToComplex(self, constraintsFuns, cubeConstraints, objFunction):
        x = []

        for x_it in range(0, self.xCount):
            l = cubeConstraints[x_it][0]
            u = cubeConstraints[x_it][1]
            r = np.random.uniform(0, 1)
            x.append(u + r * abs(u - l))
        # jako ID wystarczy podac aktualna liczbe punktow, poniewaz ID jest liczone od zera
        tmp_point = Point(x, self.pointsCount)

        self.addPoint(tmp_point, constraintsFuns,
                      cubeConstraints, objFunction, c_fun="centroid")

    def correctCentroid(self, constraintsFuns, cubeConstraints, objFunction):

        # print("Centroid znajduje sie poza obszarzem dopuszczalnym.")
        again = True
        errorFlag = False
        tmp_coounter = 0
        while again:
            x = []
            # tmp_coounter += 1
            # if tmp_coounter >= 1000:
            #     print(tmp_coounter, "razy nie udało się poprawić centroidu")
            #     break

            for x_it in range(0, self.xCount):
                l = cubeConstraints[x_it][0]
                u = cubeConstraints[x_it][1]
                x.append(np.random.uniform(l, u))

            tmp_point = Point(x, self.pointsCount)

            # Jeżeli zwróci True, to punkt znajduje sie w obszarze dopuszczalnym
            if self.checkConstraints(tmp_point, constraintsFuns,
                                     cubeConstraints):

                # print("Dodaję punkt aby wyciągnąć centroid")
                self.addPoint(tmp_point, constraintsFuns,
                              cubeConstraints, objFunction, c_fun="centroid")

                if self.pointsCount >= 100:
                    print("\nAlgorytm stworzył", self.pointsCount,
                          "punktów Complexu osiagając limit.")
                    print(
                        "Centroid nie może wydostać się z obszaru niedopuszczalnego.")
                    print("Spróbuj uruchomić algorytm jeszcze raz.")
                    return False
                    break

                worst_point = self.getWorstPoint(objFunction)
                centroid = self.centroid(worst_point)

                # Jeżeli teraz centroid znajduje się w obszarze dopuszczalnym, to koniec funkcji
                if self.checkConstraints(centroid, constraintsFuns,
                                         cubeConstraints):
                    # print("UDAŁO SIĘ WYCIAGNĄĆ CENTROID")
                    return True
                # Jeżeli teraz centroid nie znajduje się w obszarze dop, to dodajemy punkt
                else:
                    again = True
                    # print("Dodany punkt nie wyciągnął")
            # Jeżeli nie zwróciło True, to puynkt znajduje sie poza obszarem dopuszczalnym
            else:
                again = True

            # uruchamia algorytm

    def run(self, objFunction, constraintsFuns, cubeConstraints, max_it):

        counter = 0
        step_program = []
        errorFlag = False

        # print("max iteracji: ", max_it)

        # KROK 2,3
        tmpcounter2 = 0
        debug_counter_c = 0
        # dopoki warunek stopu nie jest spelniony
        while (self.convergence() == False):
            # self.plotPolygon(objFunction)
            # self.display()
            # print("kolejna iteracja")

            if self.pointsCount >= 100:
                print("Algorytm stworzył", self.pointsCount,
                      "punktów Complexu osiagając limit.")
                print("Prawdopodobnie powstało niefortunne ułożenie punktów.")
                print("Spróbuj uruchomić algorytm jeszcze raz.")
                errorFlag = True
                break

            # KROK 4
            # znajdz najgorszy punkt
            ten_konkretny_point = self.getWorstPoint(objFunction)

            # print("przed funkcją: ", end='')
            # ten_konkretny_point.display()

            # KROK 5
            # print("krok 5")
            # znajdz centroid
            centroid = self.centroid(ten_konkretny_point)

            # sprawdz, czy centroid znajduje sie w obszarze dopuszczalnym
            # jezeli nie, to dodaje punkt i wraca do poczatku petli
            if not(self.checkFunConstraints(centroid, constraintsFuns)):
                # print( "\nDodaję punkt ze względu na położenie centroidu poza obszarem dopuszczalnym")
                # self.addPointToComplex(
                #     constraintsFuns, cubeConstraints, objFunction)
                # centroid.display()
                # print()
                if self.correctCentroid(
                        constraintsFuns, cubeConstraints, objFunction):
                    # debug_counter_c += 1
                    ten_konkretny_point = self.getWorstPoint(objFunction)
                    centroid = self.centroid(ten_konkretny_point)
                    # centroid.display()
                    # continue
                else:
                    errorFlag = True
                    break

            # KROK 6
            # print("krok 6")
            # self.plotPolygon(objFunction)
            # odbij najgorszy punkt wzgledem centroidu
            self.reflect(centroid, ten_konkretny_point)

            # dopoki odbity punkt nie znajduje sie w obszarze dopuszczalnym
            # to bedzie poprawiany wewnatrz petli
            krok_7_counter = 0
            while not(self.checkConstraints(ten_konkretny_point, constraintsFuns, cubeConstraints)):
                # self.plotPolygon(objFunction)
                # KROK 7
                # print("krok 7")
                # sprawdz, ktory typ ograniczen nie jest spelniany
                con = self.checkWhichConstraints(
                    ten_konkretny_point, constraintsFuns, cubeConstraints)

                krok_7_counter += 1
                if krok_7_counter >= 101:
                    #     print("\nPSUJE SIE W KROKU 7, ", con)
                    #     print("centroid:", self.checkConstraints(
                    #         centroid, constraintsFuns, cubeConstraints), end='')
                    #     centroid.display()
                    #     self.display()
                    break

                match con:
                    case 'functions':
                        # przesuniecie do centroidu o polowe odleglosci

                        self.contract(ten_konkretny_point, centroid)

                    case 'cube':
                        # przyjecie skrajnych wartosci ograniczen
                        self.correctCubeConstraints(
                            ten_konkretny_point, cubeConstraints)

            # KROK 8
            # znajdz, jaki teraz jest najgorszy punkt
            new_worst_point = self.getWorstPoint(objFunction)

            # dopoki odbity punkt nadal jest tym najgorszym
            # to jest przesuwany w kierunku centroidu

            contract_counter = 0
            while ten_konkretny_point == new_worst_point:
                contract_counter += 1
                if contract_counter >= 5:
                    self.addPointToComplex(
                        constraintsFuns, cubeConstraints, objFunction)
                    # print(
                    #     "PSUJE SIE PRZY CONTRACT GDY ODBITY PUNKT NADAL JEST NAJGORSZY")
                    # print(
                    #     "Dodaję punkt do complexu ze względu na najgorszy punkt po odbiciu")
                    break
                self.contract(ten_konkretny_point, centroid)

                # znajdz, jaki teraz jest najgorszy punkt
                new_worst_point = self.getWorstPoint(objFunction)

            # jezeli program wyszedl z petli while, to znaczy, ze jest zaakceptowany
            # i procedura zaczyna sie od nowa

            counter += 1
            if counter == max_it:
                print("\nOsiągnięto limit iteracji:", max_it)
                break
            if counter % 500 == 0:
                # print("Counter iteracji", counter)
                # print("Dodaję punkt do complexu ze względu na licznik iteracji")
                # self.plotPolygon(objFunction)
                self.addPointToComplex(
                    constraintsFuns, cubeConstraints, objFunction)
                # self.plotPolygon(objFunction)

            step_program.append(deepcopy(self))
            # step_program[-1].display()

        # zwraca id optymalnego punktu, ktory daje najlepsza (najmniejsza) wartosc funkcji celu
        best_point = self.getBestPoint(objFunction)
        print("\nLiczba iteracji algorytmu:", counter)
        print("Liczba punktów na koniec:", self.pointsCount)
        return best_point, step_program, errorFlag

    def weights(self, objFunction):
        x1, x2, x3, x4, x5 = point.get_xi()
        for point in self.points:
            print(point.getID(), " - ", objFunction(x1, x2, x3, x4, x5))

    def correctCubeConstraints(self, point, cubeConstraints):

        p = point.get()

        # ograniczenia wpolrzednych
        for it in range(0, self.xCount):
            if p[it] < cubeConstraints[it][0]:
                p[it] = cubeConstraints[it][0]
            elif p[it] > cubeConstraints[it][1]:
                p[it] = cubeConstraints[it][1]

        point.set(p)

    def shrink(self, objFunction):

        best_point = self.getBestPoint(objFunction)

        for point in self.points:
            self.moveHalfwayTo(point, best_point)

    # sprawdza, jakiego typu ograniczen nie spelnia podany punkt

    def checkWhichConstraints(self, point, constraintsFuns, cubeConstraints):

        cubeFlag = False
        funFlag = False

        # ograniczenia funkcyjne
        funFlag = self.checkFunConstraints(point, constraintsFuns)
        if funFlag == False:
            return 'functions'

        # ograniczenia wpolrzednych
        cubeFlag = self.checkCubeConstraints(point, cubeConstraints)
        if cubeFlag == False:
            return 'cube'

        return 'none'

    def contract(self, point, centroid):
        self.moveHalfwayToCentroid(point, centroid)

    # sprawdza, czy punkt spelnia ograniczenia
    # Funkcja zwraca wartosci:
    #   – True, jezeli punkt spelnia warunki ograniczen
    #   – False, jezeli nie spelnia ograniczen

    def checkConstraints(self, point, constraintsFuns, cubeConstraints):
        if self.checkFunConstraints(point, constraintsFuns) and self.checkCubeConstraints(point, cubeConstraints):
            return True
        else:
            return False

    # sprawdza, czy dany punkt spelnia warunki ograniczen wspolrzednych
    # Funkcja zwraca wartosci:
    #   – True, jezeli punkt spelnia warunki ograniczen
    #   – False, jezeli chociaz jedna wspolrzedna nie spelnia ograniczen
    def checkCubeConstraints(self, point, cubeConstraints):

        p = point.get()

        # ograniczenia wpolrzednych
        for it in range(0, self.xCount):
            if p[it] < cubeConstraints[it][0] or p[it] > cubeConstraints[it][1]:
                return False

        # jezeli spelnia wszystkie ograniczenia wspolrzednych
        return True

    # sprawdza, czy dany punkt spelnia warunki ograniczen funkcyjnych
    # Funkcja zwraca wartosci:
    #   – True, jezeli punkt spelnia warunki ograniczen
    #   – False, jezeli punkt nie spelnia chociaz jednej funkcji ograniczen
    def checkFunConstraints(self, point, constraintsFuns):

        # sprawdza, czy punkt spelnia wszystkie funkcje ograniczen
        for function in constraintsFuns:
            x1, x2, x3, x4, x5 = point.get_xi()
            result = function(x1, x2, x3, x4, x5)

            # pierwsza funkcja ograniczen, ktora zwroci wartosc spoza obszaru powoduje zwrocenie wartosci True
            if result > 0:
                return False

        # jezeli punkt spelnia wszystkie funkcje ograniczen, to zwracana jest wartosc False
        return True

    # odbija punkt wzgledem centroidu
    def reflect(self, centroid, point):

        # pobranie wspolrzednych
        p = point.get()
        c = centroid.get()

        # wspolczynnik odbicia
        alpha = 1.3

        # nowe wspolrzedne
        x = []

        # odbicie
        for x_it in range(0, self.xCount):
            x.append((1+alpha)*c[x_it] - p[x_it]*alpha)

        # zapisanie nowych wspolrzednych
        point.set(x)
        # return Point(x, point.getID())  # -100)

    # przesuwa punkt do centrum o polowe odleglosci
    def moveHalfwayToCentrum(self, point):
        centrum = self.centrum()
        self.moveHalfwayTo(point, centrum)

    # przesuwa punkt do centroidu o polowe odleglosci
    def moveHalfwayToCentroid(self, point, centroid):
        self.moveHalfwayTo(point, centroid)

    # przesuwa punkt do drugiego punktu (niekoniecznie centroidu lub centrum) o polowe odleglosci
    def moveHalfwayTo(self, point_p, c_p):

        new_x = []

        point = point_p.get()
        point_id = point_p.getID()

        c = c_p.get()
        # print("tutaj np dziala,", point)

        # dla kolejnych wspolrzednych
        for x_it in range(0, self.xCount):

            # obliczenie polowy odleglosci wspolrzednej
            x_trans = 0.5*(c[x_it] - point[x_it])
            # x_trans = 0.5*(point[x_it] - c[x_it])

            # ustalenie nowej wartosci wspolrzednej, juz po przesunieciu
            new_x.append(c[x_it]-x_trans)
            # new_point.append(point[x_it]-x_trans)

        point_p.set(new_x)

    def move_sympyplot_to_axes(self, p, ax):
        backend = p.backend(p)
        backend.ax = ax
        # Fix for > sympy v1.5
        backend._process_series(backend.parent._series, ax, backend.parent)
        backend.ax.spines['right'].set_color('none')
        backend.ax.spines['bottom'].set_position('zero')
        backend.ax.spines['top'].set_color('none')
        plt.close(backend.fig)

    # laczy dwa punkty
    def connectPoints(self, ax, p1, p2):
        x_values = [p1[0], p2[0]]
        y_values = [p1[1], p2[1]]
        ax.plot(x_values, y_values, 'ko', linestyle='-', zorder=10)

    # laczy kolejne punkty tworzac wielokat
    def createPolygon(self, ax):
        for var_it in range(0, self.pointsCount):
            if var_it != self.pointsCount-1:
                self.connectPoints(
                    ax, self.points[var_it].get(), self.points[var_it+1].get())
            else:
                self.connectPoints(
                    ax, self.points[var_it].get(), self.points[0].get())

    # rysuje funkcje ograniczen funkcyjnych

    def plotObjFun(self, constraintsFunsString, cubeConstraints, ax):

        N = 100
        # są tylko dwa ograniczenia, bo tylko dla tylu rysujemy
        n_x1 = np.linspace(cubeConstraints[0][0], cubeConstraints[0][1], N)
        n_x2 = np.linspace(cubeConstraints[1][0], cubeConstraints[1][1], N)

        # wszystkie możliwe zmienne
        x1, x2 = sp.symbols("x1, x2")

        funs = []
        p = []
        x1_range = (x1, cubeConstraints[0][0], cubeConstraints[0][1])
        x2_range = (x2, cubeConstraints[1][0], cubeConstraints[1][1])
        if len(constraintsFunsString) == 0:
            return
        else:
            for it in range(0, len(constraintsFunsString)):

                expr = sp.parse_expr(constraintsFunsString[it] + "<=0")
                if x1 in expr.free_symbols or x2 in expr.free_symbols and len(expr.free_symbols) < 3:
                    p.append(sp.plot_implicit(expr, x1_range, x2_range,
                                              line_color="gray", alpha=1,  xlabel="", ylabel="", show=False, axis=True, margin=0, backend='matplotlib', axis_center='auto'))

                    funs.append(expr)

                    if len(p) > 1:
                        p[0].extend(p[1])

            match len(funs):
                case 1:
                    andi = sp.And(funs[0])
                case 2:
                    andi = sp.And(funs[0], funs[1])
                case 3:
                    andi = sp.And(funs[0], funs[1], funs[2])
                case 4:
                    andi = sp.And(funs[0], funs[1], funs[2], funs[3])
                case 5:
                    andi = sp.And(funs[0], funs[1], funs[2], funs[3], funs[4])

            p_andi = sp.plot_implicit(andi, x1_range, x2_range,
                                      line_color="k", alpha=1,  xlabel="", ylabel="", show=False, axis=True, margin=0, backend='matplotlib', axis_center='auto')

            p[0].extend(p_andi)
            self.move_sympyplot_to_axes(p[0], ax)

    # rysuje wielokat
    def plotPolygon(self, objFunction, constraintsFunsString, tmp_cubeConstraints, printing=False):

        fig, ax = plt.subplots()
        ax.set_title('')
        ax.set_xlabel('x1')
        ax.set_ylabel('x2')
        ax.grid(True)

        # rysuje funkcje ograniczen
        self.plotObjFun(constraintsFunsString, tmp_cubeConstraints, ax)

        # wyznacza centrum, potrzebne do wyznaczenia wsp. biegunowych
        centrum = self.centrum()

        # aktualizuje wsp. biegunowe
        self.refreshPolar(centrum)

        # sortuje wzgledem phi
        self.sortByPolar()

        # posortowane punkty sa ze soba kolejno laczone
        self.createPolygon(ax)

        worst_point = self.getWorstPoint(objFunction)

        # rysuje centroid
        centroid_p = self.centroid(worst_point)
        # print("zwrocilem juz")
        #  centroid_pAAAA.display()

        centroid = centroid_p.get()
        # print("centroid:", centroid_AAA[0])
        # print("centroid:", centroid_AAA[1])
        ax.scatter(centroid[0], centroid[1], zorder=5)

        if printing:
            plt.show()

    # rysuje wielokat ponownie
    # przydatne do wyświetlania wykresu dla danego kroku

    def plotStepPolygon(self, points, objFunction):
        fig, ax = plt.subplots()

        # rysuje funkcje ograniczen
        self.plotObjFun(ax)

        worst_point = self.getWorstPoint(objFunction)

        # rysuje centroid
        centroid_p = self.centroid(worst_point)
        # centroid_p.display()
        centroid = centroid_p.get().copy()
        ax.scatter(centroid[0], centroid[1], color="g")
        # print("centroid:", centroid)
        # print("centroid[0]", centroid[0])
        # print("centroid[1]", centroid[1])

        # wyznacza centrum, potrzebne do wyznaczenia wsp. biegunowych
        centrum = self.centrum()

        # aktualizuje wsp. biegunowe
        self.refreshPolar(centrum)

        # sortuje wzgledem phi
        self.sortByPolar()

        # posortowane punkty sa ze soba kolejno laczone
        self.createPolygon(ax)

        ax.grid(True)
        if print:
            plt.show()

    # sortuje punkt wedlug phi

    def sortByPolar(self):

        n = self.pointsCount

        it = 0
        while it < n-1:
            phi1 = self.points[it].getPhi()
            phi2 = self.points[it+1].getPhi()
            if phi1 > phi2:
                self.swap(self.points[it], self.points[it+1])

            it += 1
        n -= 1

        while n > 1:
            it = 0
            while it < n-1:
                phi1 = self.points[it].getPhi()
                phi2 = self.points[it+1].getPhi()
                if phi1 > phi2:
                    self.swap(self.points[it], self.points[it+1])
                it += 1
            n -= 1

    # zamienia dane dwoch punktow pozostawiajac jedynie ID
    def swap(self, p1, p2):
        id_1 = p1.getID()
        r1 = p1.getR()
        phi1 = p1.getPhi()

        id_2 = p2.getID()
        r2 = p2.getR()
        phi2 = p2.getPhi()

        tmp_point_1 = self.getPointFromID(id_1)
        tmp_point_2 = self.getPointFromID(id_2)
        tmp_point_1_x = tmp_point_1.get()
        tmp_point_2_x = tmp_point_2.get()

        self.points[id_1].set(tmp_point_2_x)
        self.points[id_2].set(tmp_point_1_x)

        self.points[id_1].setPolar(r2, phi2)
        self.points[id_2].setPolar(r1, phi1)

    # oblicza aktualne wartosci wspolrzednych biegunowych dla podanego punktu jako
    # poczatku ukladu wsp. biegunowych
    def refreshPolar(self, center):

        for point in self.points:

            c = center.get().copy()
            polar_x = point.get().copy()

            # wyznacza nowe wspolrzedne w ukladzie kartezjanskim, gdzie c jest srodkiem ukladu
            for x_it in range(0, self.xCount):
                polar_x[x_it] = polar_x[x_it]-c[x_it]

            # wyznacza phi oraz r w ukladzie kartezjanskim
            phi = self.phiAngle(c, polar_x)
            r = self.rDist(polar_x)

            point.setPolar(r, phi)

    # zwraca parametr r (wspolrzedne biegunowe)
    def rDist(self, polar_x):

        sum = 0
        for x_var_it in range(0, self.xCount):
            sum = np.power(polar_x[x_var_it], 2)

        return np.sqrt(sum)

    # zwraca parametr phi (wspolrzedne biegunowe)
    def phiAngle(self, c, p):

        return np.arctan2(p[0], p[1])

    def getPointFromID(self, id):

        if id > self.pointsCount:
            print("BLAD! Nie ma punktu o takim ID")
            return "BLAD! Nie ma punktu o takim ID"

        for point in self.points:
            if point.getID() == id:
                return point

    def dist(self, point1, point2):
        p1 = point1.get()
        p2 = point2.get()

        distance = 0
        for x in range(0, self.xCount):
            distance += np.power(p1[x] - p2[x], 2)

        return np.sqrt(distance)

    def distX(self, point1, point2, x_num):
        p1 = point1.get()
        p2 = point2.get()

        return abs(p1[x_num]-p2[x_num])

    # sprawdza, czy kryterium stopu jest spelnione
    def convergence(self):

        if self.checkSidesLen() <= self.epsilon:
            return True
        else:
            return False

    # zwraca dlugosc najdluzszego boku wielokata
    def checkSidesLen(self):

        result = 10000
        biggest = 0
        # kazdy punkt jest laczony z kolejnym aby ustalic dlugosc tego boku
        for point_it in range(0, self.pointsCount):

            # dlugosc boku utworzonego z ostatniego i pierwszego punktu
            if point_it == self.pointsCount-1:
                result = self.dist(self.points[point_it], self.points[0])
            # dlugosc boku utworzonego z point_it oraz point_it+1 punktu
            else:
                result = self.dist(
                    self.points[point_it], self.points[point_it+1])

            # zapisuje aktualnie najwieksza dlugosc
            if result > biggest:
                biggest = result

        return biggest

    # liczy centroid, czyli srodek wielokatu nie zawierajacego punktu dajacego najwieksza wartosc funkcji celu
    def centroid(self, worst_point):

        # lista zsumowanych poszczegolnych wspolrzednych
        sum_x_var = [0] * self.xCount
        # self.display()

        # print("Worst_point: ", end='')
        # worst_point.display()
        # lista wspolrzednych centroidu
        c = []

        # sumowanie wspolrzednych kazdego punktu poza tym najgorszym
        for point in self.points:

            # print("Teraz punkt: ", end='')
            # point.display()

            # jezeli nie jest liczone centrum, to liczony jest centroid,
            # wtedy nie bierzemy pod uwage najgorszego punktu
            if point.getID() == worst_point.getID():
                # pominiecie aktualnej iteracji petli for
                continue

            # wlasciwe sumowanie wspolrzednych punktow
            for x_var_it in range(0, self.xCount):
                sum_x_var[x_var_it] += (point.get())[x_var_it]

        # przypisanie punktowi c (centroid) jego wspolrzednych
        # wspolrzedne to srednia algebraiczna wspolrzednych punktow wierzcholkow
        for it in range(0, self.xCount):
            c.append(sum_x_var[it]/(self.pointsCount - 1))

        return Point(c, -1)

    # liczy centroid, czyli srodek wielokatu skladajacego sie ze wszystkich punktow
    def centrum(self):

        # lista zsumowanych poszczegolnych wspolrzednych
        sum_x_var = [0] * self.xCount

        # lista wspolrzednych centroidu
        c = []

        # sumowanie wspolrzednych kazdego punktu
        for point in self.points:

            # wlasciwe sumowanie wspolrzednych punktow
            for x_var_it in range(0, self.xCount):
                sum_x_var[x_var_it] += (point.get())[x_var_it]

        # przypisanie punktowi c (centrum) jego wspolrzednych
        # wspolrzedne to srednia algebraiczna wspolrzednych punktow wierzcholkow
        for it in range(0, self.xCount):
            c.append(sum_x_var[it]/self.pointsCount)

        return Point(c, -1)

    # zwraca punkt o najwiekszej wartosci funkcji celu
    def getWorstPoint(self, objFunction):
        # print("SZUKAM NAJGORSZEGO PUNKTU")
        f_max = np.NINF
        rtn_point = None

        for point in self.points:
            value = self.objFunValue(objFunction, point)
            # print("    - wartosc dla punktu ", point.getID(), " : ", value)
            if value > f_max:
                f_max = value
                rtn_point = point

        return rtn_point

    # zwraca punkt o najmniejszej wartosci funkcji celu
    def getBestPoint(self, objFunction):

        f_min = 10000000000
        rtn_point = None

        for point in self.points:  # tmp_point:
            value = self.objFunValue(objFunction, point)
            if value < f_min:
                f_min = value
                rtn_point = point

        return rtn_point

    # funkcja celu, zwraca wartosc dla danego punktu
    def constFunValue(self, constraintsFun, point):
        x1, x2, x3, x4, x5 = point.get_xi()
        return constraintsFun(x1, x2, x3, x4, x5)

    # zwraca punkt o najmniejszej wartosci funkcji celu
    def getFmin(self, objFunction):

        f_min = 10000000000
        rtn_point = None

        for point in self.points:  # tmp_point:
            value = self.objFunValue(objFunction, point)
            if value < f_min:
                f_min = value
                rtn_point = point

        return f_min

    # funkcja celu, zwraca wartosc dla danego punktu
    def objFunValue(self, objFun, point):
        x1, x2, x3, x4, x5 = point.get_xi()
        return objFun(x1, x2, x3, x4, x5)

    # wyswietla wszystkie wsp. wszystkich punktow complexu w ukladzie kartezjanskim
    def display(self):

        for point in self.points:
            print("\nPoint ID-" + str(point.getID()), end=':')
            point.display()
        print("\n")

    # wyswietla wszystkie wsp. wszystkich punktow complexu w ukladzie biegunowym
    def displayPolar(self):
        for point in self.points:
            print("\nPoint ID-" + str(point.getID()), end=':')
            point.displayPolar()
        print("\n")

    # zwraca tablice punktow complexu (listy)
    def get(self):
        tmp = []
        for it in range(0, len(self.points)):
            tmp.append((self.points[it]).get())

        return tmp
