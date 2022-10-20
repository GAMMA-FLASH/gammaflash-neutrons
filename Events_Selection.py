from google.colab import drive
drive.mount('/content/drive')

# Per gestire i dataframe
import pandas as pd

# Per le librerie matematiche
import numpy as np

# Per fare i grafici
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import seaborn as sns
from matplotlib import style
style.use('seaborn-talk')

# Per vedere la forma del file
import csv

# Espressioni regolari per leggere il file di settings
import re

# Per debug
import pdb
# pdb.set_trace()

import scipy

# Per filtro segnale
import scipy.signal

# Per eseguire lo smoothing
from scipy.signal import savgol_filter

# Per trovare i picchi
from scipy.signal import find_peaks

# Funzione per leggere il file csv
def leggi_csv(file_csv):
    # Apro il file csv
    with open(file_csv, 'r') as csvfile:
        # Creo un oggetto CSV reader
        csvreader = csv.reader(csvfile, delimiter=';')
        # Estraggo la prima riga
        prima_riga = next(csvreader)
        # Seconda riga per vedere quanto è lungo
        seconda_riga = next(csvreader)
        # Preparo header
        pre = ['BOARD', 'CHANNEL', 'TIMETAG', 'ENERGY', 'ENERGYSHORT']
        # Per la seconda prendo i valori da 0 a fine evento ogni 2 ns [0, 2, 4, 6, ...]
        tempi = [str(2 * x) for x in range(0, len(seconda_riga) - 7)]
        # Creo intestazione completa con tempi
        header = pre + tempi
    # Controllo formato file
    if prima_riga[0] == 'BOARD':
        # Leggo il file saltando la prima riga
        dataframe = pd.read_csv(file_csv, skiprows=[0], sep=';',header=None)#, nrows=100)
        # Butto le colonne che non mi servono
        dataframe.drop(dataframe.iloc[:, 5:7], inplace = True, axis = 1)
        # Metto l'header giusto
        dataframe.columns = header
    else:
        # Leggo tutto il file
        dataframe = pd.read_csv(file_csv, sep=';', header=None)#, nrows=100)
        # Butto le colonne che non mi servono
        dataframe.drop(dataframe.iloc [:, 5:7], inplace=True, axis=1)
        # Metto l'header giusto
        dataframe.columns = header
    return dataframe

# Funzione che legge i settings della misura
def prendi_metadati_misura(file_setting):
    valori = []
    # Ordine Valori
    # 0 THRESHOLD
    # 1 RECLEN
    # 2 GATESHORT
    # 3 GATE
    # 4 GATEPRE
    # 5 PRETRG
    try:
        # Apro il file di settings
        with open(file_setting, 'r') as f:
            # Leggi tutto il file
            testo_file_xml = f.read()

        # 0 THRESHOLD
        # Trova il pattern con il testo indicato
        pattern_THRESHOLD = re.compile('<key>SRV_PARAM_CH_THRESHOLD</key>.+?</value>', re.DOTALL)
        # Seleziona solamente quel testo
        risultato_THRESHOLD = re.findall(pattern_THRESHOLD, testo_file_xml)
        # In quel testo cerca una cosa composta da numeri + . + numeri
        valore_THRESHOLD = re.findall('[0-9]+\.[0-9]', risultato_THRESHOLD[0])
        # Aggiungilo a valori
        valori.append(valore_THRESHOLD[0])

        # 1 RECLEN
        pattern_RECLEN = re.compile('<key>SRV_PARAM_RECLEN</key>.+?</value>', re.DOTALL)
        risultato_RECLEN = re.findall(pattern_RECLEN, testo_file_xml)
        valore_RECLEN = re.findall('[0-9]+\.[0-9]', risultato_RECLEN[0])
        valori.append(valore_RECLEN[0])

        # 2 GATESHORT
        pattern_GATESHORT = re.compile('<key>SRV_PARAM_CH_GATESHORT</key>.+?</value>', re.DOTALL)
        risultato_GATESHORT = re.findall(pattern_GATESHORT, testo_file_xml)
        valore_GATESHORT = re.findall('[0-9]+\.[0-9]', risultato_GATESHORT[0])
        valori.append(valore_GATESHORT[0])

        # 3 GATE
        pattern_GATE = re.compile('<key>SRV_PARAM_CH_GATE</key>.+?</value>', re.DOTALL)
        risultato_GATE = re.findall(pattern_GATE, testo_file_xml)
        valore_GATE = re.findall('[0-9]+\.[0-9]', risultato_GATE[0])
        valori.append(valore_GATE[0])

        # 4 GATEPRE
        pattern_GATEPRE = re.compile('<key>SRV_PARAM_CH_GATEPRE</key>.+?</value>', re.DOTALL)
        risultato_GATEPRE = re.findall(pattern_GATEPRE, testo_file_xml)
        valore_GATEPRE = re.findall('[0-9]+\.[0-9]', risultato_GATEPRE[0])
        valori.append(valore_GATEPRE[0])

        # 5 PRETRG
        pattern_PRETRG = re.compile('<key>SRV_PARAM_CH_PRETRG</key>.+?</value>', re.DOTALL)
        risultato_PRETRG = re.findall(pattern_PRETRG, testo_file_xml)
        valore_PRETRG = re.findall('[0-9]+\.[0-9]', risultato_PRETRG[0])
        valori.append(valore_PRETRG[0])

    except:
        print('Nessun file di settings trovato')
        
    return valori


# Definisco la funzione per leggere i soli tempi T0 e TimeTag
# Li legge indifferentemente da file csv (per i T0) sia da un dataframe
def Seleziona_Tempi(origine):
    # Se è una stringa, quindi il file csv
    if isinstance(origine, str) == True: 
        file_tempi = origine
        # Legge il file csv in un dataframe
        dataframe = leggi_csv(file_tempi) 
        for j in range(len(dataframe)):
            tempi = dataframe["TIMETAG"]/1000
            # Sostituisco le virgole con i punti
            tempi = [j.replace(',', '.') for j in tempi] 
            # Trasformo i tempi in ns
            tempi = [float(j) / 1000 for j in tempi] 
            # Li faccio diventare dei float
            tempi = list(map(float, tempi)) 
        return tempi
    else:
        for j in range(len(origine)):
            tempi = list(origine ["TIMETAG"])
            tempi = [j.replace(',', '.') for j in tempi]
            tempi = [float(j) / 1000 for j in tempi]
            tempi = list(map(float, tempi))
        return tempi
        
        # Prefisso per dati sul Drive di Google
prefisso_path = "drive/MyDrive/Dati_ISIS/Selezione Eventi/Dati/Termici_T0_Th500_RL1200/"

nome_file_dati = "T_Th500_RL1200.csv"

# Nome file csv generato dal CAEN da analizzare
file_dati = prefisso_path + nome_file_dati

# Leggo tutte le finestre 
finestre = leggi_csv(file_dati)

# Leggo il file con i settings composto da 0=THRESHOLD, 1=RECLEN, 2=GATESHORT, 3=GATE, 4=GATEPRE, 5=PRETRG
setting_misura = prendi_metadati_misura(prefisso_path + 'settings.xml')

# Leggo i tempi di T0
file_T0 = prefisso_path + "T0" + nome_file_dati

# Ottengo la lista di T0
T0_tempi = Seleziona_Tempi(file_T0)

# Creo l'array che contiene i tempi valido per tutte le finestre (asse delle ascisse)
tempi_stringa = list(finestre.columns)[5:]
tempi = list(map(int, tempi_stringa))
tempi_array = np.array(tempi)   

fattore_spazio = []
eventi = []
elenco_TOF = []

# Valore di soglia per eseguire il troncamento                                                                   
soglia_taglio = 2

# Ciclo su tutte le finestre, riga per riga
for index, info_finestra in finestre.iterrows(): 
    # Prendo la colonna che contiene i dati sui TimeTag in picosecondi                                             
    TimeTag_finestra_ps = info_finestra["TIMETAG"]            
    # Prendo le varie finestrd e la colonna dei TimeTag corrispondenti                                        
    finestra = info_finestra.iloc[:][5:]                                                              
    
    # Individuo i picchi 
    picchi = find_peaks(-finestra, height=(-13600, -1200), threshold=-150, prominence = 200, distance = 100)[0]       
  
    # Plot in cui sono individuati i picchi
    plt.plot(tempi_array[picchi], finestra[picchi], '^')
    plt.plot(tempi_array, finestra)
    plt.show()

    # Cerco le aperture e le chiusure delle finestre dei singoli eventi
    aperture_eventi = []
    chiusure_eventi = []
    tempo_pre_trigger = int(float(setting_misura[5]))
    aperture_eventi = tempi_array[picchi][0:] - tempo_pre_trigger
    # Coordinata di chiusura preliminare impostata a 60 s prima del picco successivo
    chiusure_eventi = tempi_array[picchi][1:] - 60          
    ultimo_tempo = tempi_array[-1]
    chiusure_eventi = np.append(chiusure_eventi, ultimo_tempo)
    # Cerco le vere chiusure (tagliate) delle finestre eseguendo uno smoothing per vedere dove il segnale si porta attorno a zero
    chiusure_tagliate = []  
    
    # Intervallo su cui eseguire lo smoothing
    intervallo_smoothing = 81
    for p in range(0, len(aperture_eventi)):
        if aperture_eventi[p]<0:
            aperture_eventi[p] = 0
        if float(ultimo_tempo - aperture_eventi[p])/2.0 < intervallo_smoothing:
            intervallo_smoothing = 21
        if float(chiusure_eventi[p] - aperture_eventi[p])/2.0 < intervallo_smoothing:
            intervallo_smoothing = 21
            
        # Apro e chiudo la prima finestra in corrispondenza dei valori di apertura e chiusura trovati in precedenza per l'intensità degli impulsi (valori asse delle ordinate)
        impulso = finestra[int(aperture_eventi[p]/2):int(chiusure_eventi[p]/2)]                       
        impulso_filtrato = scipy.signal.filtfilt(fil_b, fil_a, impulso)
        # Smoothing del segnale con il filtro Savitzky-Golay
        impulso_smooth = savgol_filter(impulso, window_length = intervallo_smoothing, polyorder = 1)         
        # Prendo la finestra di interesse anche per le coordinate temporali (asse delle ascisse)
        tempi_impulso = tempi[int(aperture_eventi[p]/2):int(chiusure_eventi[p]/2)]      

        # Da qui inizio la parte per la valutazione della coda dell'impulso da tagliare
        # Parto dalla fine del segnale e vado indietro
        i = -1                                                                                      
        deviazioni = []   
        # Lista di valori di tempi a cui eseguire il taglio ottenuti dal calcolo delle deviazioni standard                                                                                             
        tempi_inizio_taglio = []                                                                      
        while tempi_impulso[i] > aperture_eventi[p]+30:   
            # Vado indietro nei tempi a passi di 20 s
            j = i - 20        
            # Nella serie degli impulsi prendo quelli compresi tra i valori di j e i che definiscono questi nuovi intervalli
            finestra_taglio = impulso_smooth[j:i]    
                
            # Eseguo la deviazione standard dei valori degli impulsi nelle varie finestre   
            deviazioni.append(np.std(finestra_taglio))      
                print(np.std(finestra_impulso), tempi_impulso[i], i)    
            tempi_inizio_taglio.append(tempi_impulso[i])
            # Scalo l'indice i a passi di 10 ns in modo tale da prendere una sovrapposizione tra le finestre (per non tagliarle ogni 20 ns)
            i = i - 10      
        # Eseguo le differenze tra le deviazioni standard per vedere di quanto variano l'una rispetto all'altra
        diff_std = []
        for k in range(1, len(deviazioni)):
            diff = deviazioni[k-1] - deviazioni[k]
            media = (deviazioni[k-1] + deviazioni[k])*0.5
            diff_std.append(abs(diff))     
        plt.plot(diff_std, color = 'blue', label='deviazioni standard')
        plt.legend(loc='upper left')
        plt.show()
        deviazioni_arr = np.array(diff_std)  
        # Cerco i valori di deviazione standard inferiori a una certa soglia per vedere dove poter chiudere le finestre, sotto forma di un array logico
        deviazioni_min = (deviazioni_arr < soglia_taglio)*1   
        # Controllo dove ci sono i valori di deviazione standard maggiori della soglia
        controllo = np.where(deviazioni_min == 0)    
        # Primo indice a cui trovo valori di deviazione standard maggiori della soglia
        try:
            indice = controllo[0][0]
        except:
            indice = 0   
        tempo_taglio = tempi_impulso[indice]   
        # Coordinata temporale a cui si chiude la finestra in corrispondenza del primo valore di deviazione maggiore della soglia ( quindi dell'ultimo inferiore)
        tempo_chiusura_evento = tempi_inizio_taglio[indice]   
        # Valore della coordinata temporale a cui trovo la prima deviazione minore della soglia
        valore_tempo = np.where(np.array(tempi_impulso) == tempo_chiusura_evento)
        # Lista contenente tutte le chiusure dopo il troncamento
        chiusure_tagliate.append(tempi_impulso[valore_tempo[0][0]])

    # Valuto la lunghezza complessiva delle finestre tagliate, per capire quanto è stato il risparmio in termini di spazio
    fattore_spazio.append(sum(chiusure_tagliate - aperture_eventi)/(len(finestra)*2))

    # Riscrivo il valore di time tag definito in nanosecondi
    TimeTag_finestra_ns = float(TimeTag_finestra_ps/1000)
    TimeTag_finestra_ns = int(float(TimeTag_finestra_ps.replace(",","."))/1000)
    # Eseguo le differenze tra valori di T0 e TimeTag
    differenze_all = np.array([i - TimeTag_finestra_ns for i in T0_tempi])      
    # Controllo quali sono i tempi negativi, quindi venuti prima dell'i-esimo T0
    controllo = (differenze_all) < 0     
    # Ne sommo la quantità così da ottenere quanti sono
    quanti = controllo.sum()   
    if quanti==0:
        continue   
    # T0 relativo alla finestra che sto cercando       
    T0_finestra = T0_tempi[quanti-1]     
    # Delta assoluta della finestra: differenza tra il primo Time tag e il T0
    delta = TimeTag_finestra_ns - T0_finestra    
    # Tempo di volo (TOF): delta + coordinata temporale di apertura finestra (*2 per trasformarla da posizione a tempo, essendo il campionamento ogni 2 ns)
    TOF = np.array([delta + j*2 for j in aperture_eventi])      
    elenco_TOF.append(TOF)

    # Valori di intensità degli impulsi delle varie finestra
    finestra_list = finestra.tolist()     
    for h in range(len(TOF)):
        # Se l'evento è più corto di 460 ns (2 volte il tempo di decadimento), ignoralo e passa oltre
        if chiusure_tagliate[h] - aperture_eventi[h] < 500:
            continue
        impulso_completo = []
        # L'impulso completo è formato dal TOF relativo alla finestra e dai valori di intensità degli impulsi compresi nei range di apertura e chiusura stabiliti
        impulso_completo.append([int(TOF[h])])    
        impulso_completo.append(finestra_list[int(aperture_eventi[h]/2):int(chiusure_tagliate[h]/2)])
        # Creo un'unica lista con tutti i dati che mi servono sugli impulsi completi  
        flat_evento_completo = [numero for lista in impulso_completo for numero in lista]    
        eventi.append(flat_evento_completo)
    # Stampo tutti gli eventi estratti, formati dall'impulso completo e il TOF associato a ognuno    
    print(eventi)

    # Plot completo dei singoli eventi, con i picchi e le coordinate di apertura e chiusura delle finestre temporali
    # Evento
    plt.plot(tempi_array, finestra,'k')
    # Picchi
    plt.plot(tempi_array[picchi], finestra[picchi], '^r')
    # Coordinate di apertura della finestra
    plt.vlines(x = [i for i in aperture_eventi], ymin = min(finestra), ymax = max(finestra), color = 'g')
    # Coordinate di chiusura (tagliate) della finestra
    plt.vlines(x = [l for l in chiusure_tagliate], ymin = min(finestra), ymax = max(finestra), color = 'b')
    plt.show()
    # Stampo anche l'indice relativo all'evento
    print(index)

# Tempi di volo
TOFs = [TOF for singoli_TOF in elenco_TOF for TOF in singoli_TOF] 

# Creo il file di output che conterrà tutti gli eventi singoli con le informazioni sul TOF e gli impulsi
file_output = 'Eventi_' + nome_file_dati

file_output_completo = prefisso_path + file_output

with open(file_output_completo, 'w') as file:
    write = csv.writer(file, delimiter=',')
    write.writerows(eventi)
