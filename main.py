import matplotlib.pyplot as plt
import numpy as np
from point import Point
from complex import Complex
from interface import *
from math import *
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from funcParser import getFunction, getFunctionString
import traceback

# Przed wpisaniem tej komendy trzeba zmienić nazwę main.py na MetodaComplex.py
# pyinstaller -F -w --onefile --icon=ikona.ico MetodaComplex.py


def info(thing):
    print("\033[92m", thing, "\033[0m")


def clear_canvas(figure):
    figure.get_tk_widget().forget()
    plt.close('all')


def draw_figure(canvas, figure, values):
    # plt.xlim(float(values["xmin"]), float(values["xmax"]))
    # plt.ylim(float(values["ymin"]), float(values["ymax"]))
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    widget = figure_canvas_agg.get_tk_widget()
    figure_canvas_agg.draw()
    widget.pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def okienko():
    cubeConstraints = []
    constraintsFuns = []
    constraintsFunsString = []
    cubeConstr_list_print = []
    constraintsFuns_print = []
    figure = None
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)
        try:

            if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
                break
            if event == "Dodaj-kostka":
                # sprawdzenie czy można uruchomić
                if len(cubeConstr_list_print) == 5:
                    sg.Print(f'Wprowadzono już limit ograniczeń kostki!')
                    continue
                if str(values['LowerConstr']) == "" or str(values['UpperConstr']) == "":
                    sg.Print(f'Nie wprowadzono ograniczenia/ń zmiennej!')
                    continue

                print('Dodano ograniczenie kostki')
                cubeConstraints.append(
                    [float(values['LowerConstr']), float(values['UpperConstr'])])
                cubeConstr_list_print = (make_cubeConstr_list(cubeConstraints))
                window['List-kostka'].update(cubeConstr_list_print)

            if event == "Dodaj-funkcja":
                # sprawdzenie czy można uruchomić
                if len(constraintsFuns_print) == 5:
                    sg.Print(f'Wprowadzono już limit ograniczeń funkcyjnych!')
                    continue
                if str(values['-funConstr-']) == "":
                    sg.Print(f'Nie wprowadzono ograniczenia funkcyjnego!')
                    continue

                print('Dodano ograniczenie funkcyjne')
                constraintsFuns_print.append(values['-funConstr-'])
                constraintsFunsString.append(
                    getFunctionString(values['-funConstr-']))
                window['List-funkcje'].update(constraintsFuns_print)
                window['-funConstr-'].update("")

            # Uruchomnienie algorytmu
            if event == "Uruchom":
                if(figure):
                    clear_canvas(figure)

                plt.clf()

                # sprawdzenie czy można uruchomić
                if len(cubeConstraints) < 2:
                    sg.Print(
                        f'Wprowadź ograniczenia zmiennych!')
                    continue

                if (not(values["xmax"]) and values["xmin"]) or (not(values["xmin"]) and values["xmax"]):
                    sg.Print(
                        f'Wprowadź oba ustawienia wykresu dla osi OX albo pozostaw pola puste dla wartości automatycznych!')
                    continue
                if (not(values["ymax"]) and values["ymin"]) or (not(values["ymin"]) and values["ymax"]):
                    sg.Print(
                        f'Wprowadź oba ustawienia wykresu dla osi OY albo pozostaw pola puste dla wartości automatycznych!')
                    continue

                # algorytm
                print("\nUruchomiono algorytm")

                # inicjacja granic wyświetlanego wykresu
                if not(values["xmax"]):
                    window["xmax"].update(str(cubeConstraints[0][1]))
                    values["xmax"] = cubeConstraints[0][1]

                if not(values["xmin"]):
                    window["xmin"].update(str(cubeConstraints[0][0]))
                    values["xmin"] = cubeConstraints[0][0]

                plt.xlim(float(values["xmin"]), float(values["xmax"]))

                if not(values["ymax"]):
                    window["ymax"].update(str(cubeConstraints[1][1]))
                    values["ymax"] = cubeConstraints[1][1]

                if not(values["ymin"]):
                    window["ymin"].update(str(cubeConstraints[1][0]))
                    values["ymin"] = cubeConstraints[1][0]

                plt.ylim(float(values["ymin"]), float(values["ymax"]))

                # przypisywanie wartości z okna do zmiennych
                epsilon = float(values['-epsilon-'])
                max_it = int(values['-max-it-'])

                # parsowanie funkcji i zwracanie ilości zmiennych
                objectiveFun, amount_of_xs = getFunction(
                    values['combo-objFun'])

                if not (amount_of_xs <= len(cubeConstraints)):
                    sg.Print(
                        f'Liczba ograniczeń koski nie zgadza się z liczbą zmiennych!\nKażda zmienna musi mieć swoje ograniczenie')
                    continue

                constraintsFuns = []
                # NIE RUSZAĆ TMP
                for ogr in constraintsFuns_print:
                    funs, tmp = getFunction(ogr)
                    constraintsFuns.append(funs)

                # operacje na kompleksie
                kompleks = Complex()
                kompleks.fill(cubeConstraints, constraintsFuns,
                              objectiveFun, epsilon)
                best_point, step_prog, errorFlag = kompleks.run(
                    objectiveFun, constraintsFuns, cubeConstraints, max_it)
                print("\nZnaleziony optymalny punkt:")
                best_point.display(mode="multirow")
                print("\nWartość funkcji celu dla znalezionego punktu:")
                print("", kompleks.getFmin(objectiveFun))
                print("\nWartość funkcji ograniczeń dla znalezionego punktu:")
                for it in range(0, len(constraintsFuns)):
                    print(" g" + str(it+1) + ":",
                          kompleks.constFunValue(constraintsFuns[it], best_point))
                if errorFlag:
                    print("\nUWAGA!")
                    print("Algorytm nie zakończył działania poprzez kryterium stopu.")
                    print("Znaleziony punkt może nie być rozwiązaniem.")
                    print(
                        "Sprawdź komunikaty powyżej, aby dowiedzieć się, co było przyczyną.")

                # rysowanie wykresu jeżeli funkcja celu ma dwie zmienne
                if amount_of_xs == 2:
                    kompleks.plotPolygon(
                        objectiveFun, constraintsFunsString, cubeConstraints, printing=False)
                    makeKolorki(objectiveFun, values)

                    figure = draw_figure(
                        window['-PLOT_CANV-'].TKCanvas, plt.gcf(), values)
                    plt.xlim(float(values["xmin"]), float(values["xmax"]))
                    plt.ylim(float(values["ymin"]), float(values["ymax"]))

                    # kroki i slajder init
                    window["slider-kroki"].update(range=(0, 0))
                    window["slider-kroki"].update(range=(0, len(step_prog)))
                    window['-kroki-'].update(len(step_prog))

                # w przeciwnym przypadku nie rysujemy wyresów
                else:
                    window['-kroki-'].update(
                        "Kroki wyświetlane tylko dla funkcji dwóch zmiennych")
                    plt.text(0, 0, "Brak wykresu", size=30, rotation=0,
                             ha="center", va="center",
                             color="#FDCB52",
                             bbox=dict(boxstyle="round",
                                       ec="#2C2825",
                                       fc="#705E52",
                                       )
                             )
                    figure = draw_figure(
                        window['-PLOT_CANV-'].TKCanvas, plt.gcf(), values)

            # obsluga poruszania slajderem
            if event == "slider-kroki":
                if(figure):
                    clear_canvas(figure)

                    plt.clf()
                    krok = int(values['slider-kroki'])
                    krok_minus = krok - 1
                    step_prog[krok_minus].plotPolygon(
                        objectiveFun, constraintsFunsString, cubeConstraints, printing=False)
                    makeKolorki(objectiveFun, values)
                    plt.xlim(float(values["xmin"]), float(values["xmax"]))
                    plt.ylim(float(values["ymin"]), float(values["ymax"]))
                    figure = draw_figure(
                        window['-PLOT_CANV-'].TKCanvas, plt.gcf(), values)

            # obsluga przycisku odzwiez, który aktualizuje wykres wzgledem ustawien
            # bez uruchamiania algorytmu
            if event == "odswiez-wykres":
                if(figure):
                    clear_canvas(figure)
                    plt.clf()
                    krok = int(values['slider-kroki'])
                    krok_minus = krok - 1
                    step_prog[krok_minus].plotPolygon(
                        objectiveFun, constraintsFunsString, cubeConstraints, printing=False)
                    makeKolorki(objectiveFun, values)
                    plt.xlim(float(values["xmin"]), float(values["xmax"]))
                    plt.ylim(float(values["ymin"]), float(values["ymax"]))
                    figure = draw_figure(
                        window['-PLOT_CANV-'].TKCanvas, plt.gcf(), values)

            # usuwanie zaznaczonego przedziału w liscie ogr. kostki
            if event == 'Usun-kostka' and values['List-kostka']:
                print("Usunięto ogr. kostki ", values['List-kostka'][0])
                id = cubeConstr_list_print.index(values['List-kostka'][0])
                cubeConstraints.pop(id)
                cubeConstr_list_print = make_cubeConstr_list(cubeConstraints)
                window['List-kostka'].update(cubeConstr_list_print)

            # usuwanie zaznaczonej funkcji w liscie ogr. funkc.
            if event == 'Usun-funkcja' and values['List-funkcje']:
                print("Usunięto ogr. funkcyjne ", values['List-funkcje'][0])
                id = constraintsFuns_print.index(values['List-funkcje'][0])
                constraintsFuns_print.remove(values['List-funkcje'][0])
                constraintsFunsString.pop(id)
                window['List-funkcje'].update(constraintsFuns_print)

            # czyszczenie okna z outputem
            if event == "Wyczysc-logi":
                window['logi'].update('')

        # obsluga bledow
        except Exception as e:
            tb = traceback.format_exc()
            sg.Print(f'An error happened.  Here is the info:', e, tb)

    window.close()

# funkcja do tworzenia i wyswietlania warstwicy funkcji felu na aktualnym wykresie


def makeKolorki(objectiveFun, values):
    plt.xlim(float(values["xmin"]), float(values["xmax"]))
    plt.ylim(float(values["ymin"]), float(values["ymax"]))
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    x = np.linspace(xmin, xmax)
    y = np.linspace(ymin, ymax)
    X, Y = np.meshgrid(x, y)
    Z = objectiveFun(X, Y)
    Z = np.array(Z)
    Z = np.reshape(Z, (len(x), len(y)))

    cnt = plt.contourf(X, Y, Z, extend='both', levels=500,
                       cmap="rainbow", alpha=0.8)
    for c in cnt.collections:
        c.set_edgecolor("none")
        c.set_linewidth(0.00000000000000000000000001)

    plt.colorbar()

# main


def main():
    okienko()


main()
