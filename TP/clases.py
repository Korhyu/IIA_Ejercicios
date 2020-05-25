

class individuo():
    #Parametros del filtro
    param = [0, 0, 0, 0, 0]

    #Puntaje del individuo
    score = 0

    #Curva resultado del filtro
    filtrada = []
    
    """ Alternativa
    # Para el caso del filtro por tratarse de 5 datos con nombre uso un diccionario para almacenar los valores
    # de los distintos parametros del filtro de esta forma cada individuo tiene el nombre del parametro
    parametros = dict(N=0, gamma=0, alfa=0, Nmax=0, Nmin=0)
    """

    
    def __init__(self, parametros=None):
        self.param = parametros


    def set_score(self, sc_ind):
        self.score = sc_ind

    def get_filt(self, filtrada):
        self.filtrada = filtrada.copy()