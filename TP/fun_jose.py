from clases import individuo
import numpy as np
import random
import csv
import math
import matplotlib.pyplot as plt

pais = "ar"


def load_data():
    #Lee los datos del archivo "ar_COVID.csv" y devuele en el vector los datos de los contagios nuevos por dia
    archivo = pais + "_COVID.csv"
    
    with open(archivo) as file:
        datos = []
        reader = csv.reader(file)
        reader = csv.DictReader(file)   #Cargo los encabezados en el lector del archivo
        #next(reader, None)              #Salteo la fila de encabezados
        for fila in reader:
            datos.append(int(fila['New']))
        
        return np.array(datos)


def gen_signal(amp, per, fases, muestras):
    # Recibe las amplitudes, periodos y fases como vectores y el numero de muestras es un int.
    # devuelve la señal como suma de todos los senos usando los parametros antes dados.
    # Los periodos indicados son la cantidad de muestras necesarias para un ciclo de senoidal

    if len(amp) != len(per) and len(amp) != len(fases):
        #Verifico que los vectores sean del mismo tamaño
        print("Los vectores de amplitud, frecuencia y fase deben tener la misma cantidad de elementos")
        return None
    
    s = np.empty([len(amp), muestras]) 

    for i in range(len(amp)):
        for j in range(muestras):
            s[i,j] = amp[i] * math.sin(2 * math.pi * j / per[i])

    st = np.empty(muestras) 
    for j in range(muestras):
        st[j] = sum(s[:,j])

    # Le monto una continua para ver si eso es lo que rompe el sigma
    #if st.min() < 0:
    #    st = st - st.min()

    #plt.plot(s.transpose(), label = "original")
    #plt.plot(st, label = "suma")
    #plt.legend()
    #plt.show()

    return st

def add_noise(amp, st):
    #Agrega ruido aleatorio de amplitud especificada y desplaza la señal completa para no tener valroes negativos
    
    n = np.random.default_rng().uniform(low=-amp, high=amp, size=len(st))

    st = st + n

    #if st.min() < 0:
    #    st = st - st.min()
    
    #plt.plot(n, label = "noise")
    #plt.plot(st, label = "signal")
    #plt.legend()
    #plt.show()

    return st


def FiltroDEWMA(param, data):
    '''Variable: Array a calcular, N: factor de aprendizaje, gama: Velocidad de adaptacion, alfa: Coeficiente de estabilizacion, Nmax y Nmin valores limite para N'''

    N = param[0]
    gama = param[1]
    alfa = param[2]
    sigma = param[3]
    Nmax = param[4]
    Nmin = param[5]

    variable = data


    DEWMA = np.array([variable[0]])
    Ns = [N]
    for j in range(1,len(variable)):
        #sigma = 2 * (DEWMA[j-1])**(1/2)
        sigma = 2 * (abs(DEWMA[j-1]))**(1/2)
        #sigma = sigma / (2 * (DEWMA[j-1])**(1/2))
        error = abs(variable[j]-DEWMA[j-1])
        if error > sigma:
            N = round(N/gama)
            if N < Nmin:
                N = Nmin
        if error < sigma/alfa: 
            N = round(N * gama)
            if N > Nmax:
                N = Nmax
        if N < Nmin:
            N = Nmin
        elif N > Nmax:
            N = Nmax
        Ns.append(N)
        a = DEWMA[j-1] +(variable[j]-DEWMA[j-1])/N
        DEWMA = np.append( DEWMA , np.array(a))


    param[0] = N
    param[1] = gama
    param[2] = alfa
    param[3] = sigma

    return DEWMA


def FiltroFIR(N, variable):
    #Filtro FIR con N variable
    N = int(N)
    inicio = variable[0:N]
    FIR = np.zeros(N)
    FIR[N-1] = np.average(inicio)
    for j in range(0,len(variable)-N):
        a =FIR[N+j-1] +(variable[j+N]-variable[j])/N
        FIR = np.append( FIR , np.array(a ))
    return FIR


def run_test(param, data):
    #Funcion que corre los 5 parametros recividos como lista en el filtro DEWMA
    #deve devolver la curva resultado del filtro
    #este filtro debe recivir el vector de valores de contagio del COVID

    return FiltroDEWMA(param, data)




def plot_filtrados(pobl, orig, filtr, ind_min, ind_max, gen=None):
    #Funcion auxiliar para ploteo de las salidas de toda la poblacion del filtro DEWMA

    archivo = "Evolucion/Gen" + str(gen) + ".png"
    fig = plt.figure(figsize=(12,10))
    plt.ylabel('Valor')
    plt.xlabel('Tiempo')
    plt.title('Resultados de Generacion')

    plt.plot(orig, 'k--', label='Datos sin Ruido')
    for ind in range(len(pobl)):

        #Elimino los decimales de los parametros
        param = pobl[ind].round(decimals=2) 
        legend = ' '.join(map(str, param)) 
        plt.plot(filtr[ind], label = legend)
        
    plt.legend(loc=4)


    if archivo is None:
        plt.show()
    else:
        plt.savefig(archivo)
        plt.close()


    #Impresion del mejor y peor individuo de la generacion
    archivo = "Evolucion/GenWB" + str(gen) + ".png"
    fig = plt.figure(figsize=(12,10))
    plt.ylabel('Valor')
    plt.xlabel('Tiempo')
    plt.title('Resultados Peor y Mejor de la Generacion')
    plt.plot(orig, 'k--', label='Datos sin Ruido')

    #Mejor individuo
    param = pobl[ind_min].round(decimals=2) 
    legend = ' '.join(map(str, param)) 
    plt.plot(filtr[ind_min], label = legend)
    #Peor individuo
    param = pobl[ind_max].round(decimals=2) 
    legend = ' '.join(map(str, param)) 
    plt.plot(filtr[ind_max], label = legend)

    plt.legend(loc=4)

    if archivo is None:
        plt.show()
    else:
        plt.savefig(archivo)
        plt.close()


def plot_FIR(entrada, salida_FIR, salida_DEWMA, gen, rango = None):
    #Funcion que plotea la salida del filtro FIR comparandola con la salida DEWMA

    if rango is not None:
        FIR = salida_FIR[rango[0]:rango[1]]
        DEWMA = salida_DEWMA[0, rango[0]: rango[1]]
        entrada = entrada[rango[0]:rango[1]]
    else:
        FIR = salida_FIR
        DEWMA = DEWMA[0,:]

    archivo = "Evolucion/Comparacion" + str(gen) + ".png"
    fig = plt.figure(figsize=(12,10))
    plt.ylabel('Valor')
    plt.xlabel('Tiempo')
    plt.title('Comparacion entre FIR y DEWMA a igual N')
    plt.plot(entrada, 'k--', label='Datos sin Ruido')
    plt.plot(FIR, label = "FIR")
    plt.plot(DEWMA, label = "DEWMA")
    plt.legend(loc=4)
    plt.savefig(archivo)
    plt.close()

    


    '''Incertar subploteo aca como segunda parte de esta funcion a todo ponerles nombres 
    distinto de archivo con alguna diferencia para que no se pisen
    Son todas ideas eh... fijate cuales te parecen piolas y si se te ocurren mas
        -Ploteo con la señal original y sin ruido
        -Ploteo con la señal original, el mejor de la poblacion y el peor
        -Ploteo de los errores (diferencia entre señal y salida del filtro) ya estan en el vector
        -Error maximo (un color), minimo (otro color) y promedio (otro color) de la generacion

    '''

def plot_error(evol_error, error_max, error_min, datos_puros, datos_orig):
    #Funcion que genera el ploteo de la evolucion del error
    plt.figure(figsize=(14, 10))

    plt.subplot(311)
    plt.plot(datos_orig, label='Señal con ruido')
    plt.plot(datos_puros, label='Señal sin ruido')
    plt.ylabel('Valor')
    plt.xlabel('Tiempo')
    plt.grid(True)
    plt.legend(loc=4)

    plt.subplot(312)
    plt.plot(evol_error, label='Medio generacional')
    plt.plot(error_max, label='Maximo generacional')
    plt.plot(error_min, label='Minimo generacional')
    plt.ylabel('Error')
    plt.xlabel('Generacion')
    plt.grid(True)
    plt.legend(loc=1)


    plt.subplot(313)
    plt.plot(evol_error, label='Medio generacional')
    plt.plot(error_min, label='Error minimo por generacion')
    plt.suptitle('Evolucion del error generacional')
    plt.ylabel('Error')
    plt.xlabel('Generacion')
    plt.grid(True)
    plt.legend(loc=1)
    plt.savefig("Evolucion/Error.png")
    plt.close()