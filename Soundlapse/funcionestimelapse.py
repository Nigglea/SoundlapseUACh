# -*- coding: utf-8 -*

'''
Herramientas para el TimeLapse

Luis Alvarado. 2017.
Diego Espejo 2019.
'''

import math
import numpy as np
import numpy.matlib
import sys


def get_nchunks(len_in_sig, m_inic_desc, m_segment, m_desc):
    'Calcular Cantidad de muestras en Soundlapse'
    len_timelapse = 0
    idx           = m_inic_desc
    n_chunks      = 0
    # Calcular la cantidad de muestras que tendra el timelapse y la cantidad de trozos (chunks)
    while idx < len_in_sig:
        idx += m_segment + m_desc
        if idx >= len_in_sig:
            break
        len_timelapse += m_segment
        n_chunks += 1
    
    return n_chunks
def get_nchunks_cal(len_in_sig, m_inic_desc, m_segment, m_desc):
    'Calcular Cantidad de muestras en Soundlapse'
    len_timelapse = 0
    idx           = m_inic_desc
    n_chunks      = 0
    # Calcular la cantidad de muestras que tendra el timelapse y la cantidad de trozos (chunks)
    while idx <= len_in_sig:
        idx += m_segment + m_desc
        if idx >= len_in_sig:
            break
        len_timelapse += m_segment
        n_chunks += 1
    m_pass=len_in_sig-idx
    return n_chunks,m_pass


def get_cross_out(crossfade_type):
    'Anunciar que tipo de crossfade se utilizará'
    if crossfade_type == 1:
        print ("Ha escogido fade lineal.")
        cross_out = 'lineal'
    elif crossfade_type == 2:
        print ("Ha escogido fade exponencial.")
        cross_out = 'exponencial'
    elif crossfade_type == 3:
        print ("Ha escogido fade logarítmico.")
        cross_out = 'log'
    else:
        print ("Error de tipo de fade.")
        exit()
    return cross_out


def get_crossfaders(crossfade_type, m_fades,stereo):
    '''Creacion de curvas de crossfaders
    de acuerdo a lo ingresado desde el script principal'''
    if stereo==True:
        if crossfade_type == 1:  # Lineal
            fadein_vect    = np.transpose(numpy.matlib.repmat(np.linspace(0, 1, m_fades), 2, 1))
            fadeout_vect   = np.transpose(numpy.matlib.repmat(np.linspace(1, 0, m_fades), 2, 1))
            cross_out      = "lineal"
        elif crossfade_type == 2:  # Exponencial
            linear_vector  = np.arange(m_fades)
            linear_vector  = np.divide(linear_vector, float(m_fades))
            exp_vector     = np.exp(linear_vector)
            exp_vector     = np.divide(exp_vector, np.max(exp_vector))
            exp_vector_neg = np.flipud(exp_vector)
            fadein_vect    = np.transpose(numpy.matlib.repmat(exp_vector, 2, 1))
            fadeout_vect   = np.transpose(numpy.matlib.repmat(exp_vector_neg, 2, 1))
            cross_out      = "exponencial"

        elif crossfade_type == 3:  # Logaritmico        
            linear_vector  = np.linspace(1, math.exp(1), m_fades)
            log_vector     = np.log(linear_vector)
            log_vector     = np.divide(log_vector, np.max(log_vector))
            log_vector_neg = np.flipud(log_vector)
            fadein_vect    = np.transpose(numpy.matlib.repmat(log_vector, 2, 1))
            fadeout_vect   = np.transpose(numpy.matlib.repmat(log_vector_neg, 2, 1))
            cross_out      = "logaritmico"
        else:
            print ("Error, tipo de crossfading no asignado.")
            return -1
    else:
        if crossfade_type == 1:  # Lineal
            fadein_vect    = np.transpose(np.linspace(0, 1, m_fades))
            fadeout_vect   = np.transpose(np.linspace(1, 0, m_fades))
            cross_out      = "lineal"
        elif crossfade_type == 2:  # Exponencial
            linear_vector  = np.arange(m_fades)
            linear_vector  = np.divide(linear_vector, float(m_fades))
            exp_vector     = np.exp(linear_vector)
            exp_vector     = np.divide(exp_vector, np.max(exp_vector))
            exp_vector_neg = np.flipud(exp_vector)
            fadein_vect    = np.transpose(exp_vector)
            fadeout_vect   = np.transpose(exp_vector_neg)
            cross_out      = "exponencial"
        elif crossfade_type == 3:  # Logaritmico        
            linear_vector  = np.linspace(1, math.exp(1), m_fades)
            log_vector     = np.log(linear_vector)
            log_vector     = np.divide(log_vector, np.max(log_vector))
            log_vector_neg = np.flipud(log_vector)
            fadein_vect    = np.transpose(log_vector)
            fadeout_vect   = np.transpose(log_vector_neg)
            cross_out      = "logaritmico"
        else:
            print ("Error, tipo de crossfading no asignado.")
            return -1
    return fadein_vect, fadeout_vect, cross_out


def time_to_samples(in_time_inicio, in_time_segment, in_time_delta, in_time_fade, samp_freq):
    '''     Inputs:
    in_time_inicio en minutos
    in_time_segment en segundos
    in_time_delta en minutos
    in_time_fade en segundos
    '''
    ''' 
        Conversion de minutos a segundos
    '''
    in_time_inicio = in_time_inicio*60
    time_delta = in_time_delta * 60
    '''
        Time to samples.
    '''
    m_desc         = int(time_delta * samp_freq )      # muestras descartadas entre chunks
    m_fades        = int(in_time_fade * samp_freq)     # muestras con crossfading
    m_inic_desc    = int(in_time_inicio * samp_freq)   # muestras descartadas del inicio
    m_timelapse    = int(in_time_segment * samp_freq)  # muestras por cada chunk
    return m_desc, m_fades, m_inic_desc, m_timelapse


def get_timelapse_one_file(in_sig, n_chunks, fadein_vect, fadeout_vect, m_inic_desc, m_segment, m_desc, m_fades,
                           time_lapse_vector, filez, filepath, chunk_fadeout, cont):
    '''Creacion de vector que contiene las muestras seleccionadas de el(los) archivo(s) original(es)'''
    if n_chunks == 0:  
        # Si es que se presenta un archivo que por duración no entrega segmentos al timelapse.
        # Se debe proteger la línea siguiente.
        time_lapse_vector  = np.concatenate((time_lapse_vector, chunk_fadeout))
        progress_per_chunk = 1.0
        cont              += progress_per_chunk
        percent_progress   = cont / len(filez) * 100
        sys.stdout.write("\rProgreso: " + str(percent_progress) + '%. ')                            # Barra de progreso.
        sys.stdout.flush()
    for kdx in range(n_chunks):
        if kdx == 0:
            if filepath == filez[0]:                                                                #### Primer segmento del primer archivo.
                in_sig.read(m_inic_desc)                                                                # Descarta primeras muestras
                chunk_inicio      = np.multiply(in_sig.read(m_fades), fadein_vect)                      # Fade-in inicial
                frames            = m_segment - 2 * m_fades                                             # Largo del segmento
                chunk             = in_sig.read(frames)                                                 # Primer segmento.
                time_lapse_vector = np.concatenate((time_lapse_vector, chunk_inicio, chunk))            # Concatenación de vectores.
            if filepath != filez[0]:                                                                #### Primer segmento de archivos no-primeros.
                chunk_fadein      = np.multiply(in_sig.read(m_fades), fadein_vect)                      # 
                chunk_fade        = chunk_fadein + chunk_fadeout                                        #
                chunk = in_sig.read(m_segment - 2 * m_fades)                                            #
                time_lapse_vector = np.concatenate((time_lapse_vector, chunk_fade, chunk))              #
        if kdx == n_chunks - 1:                                                                     #### Último segmento de archivos no-últimos.
            if filepath != filez[len(filez) - 1]:                                                   #### Último segmento de archivos no-últimos.
                chunk_fadeout     = np.multiply(in_sig.read(m_fades), fadeout_vect)                     #
                in_sig.read(m_desc)                                                                     #
                chunk_fadein      = np.multiply(in_sig.read(m_fades), fadein_vect)                      #
                chunk_fade        = chunk_fadein + chunk_fadeout                                        #
                chunk             = in_sig.read(m_segment - 2 * m_fades)                                #
                time_lapse_vector = np.concatenate((time_lapse_vector, chunk_fade, chunk))
                chunk_fadeout     = np.multiply(in_sig.read(m_fades), fadeout_vect)                     # Último Fade-Out de archivos no-últimos
            if filepath == filez[len(filez) - 1]:                                                   #### Último segmento del último archivo.
                chunk_fadeout     = np.multiply(in_sig.read(m_fades), fadeout_vect)                     # Penúltimo Fade-Out
                in_sig.read(m_desc)                                                                     # Descarta muestras
                chunk_fadein      = np.multiply(in_sig.read(m_fades), fadein_vect)                      # Último Fade-In
                chunk_fade        = chunk_fadein + chunk_fadeout                                        # Último Crossfade
                chunk             = in_sig.read(m_segment - 2 * m_fades)                                # Último Segmento
                chunk_final       = np.multiply(in_sig.read(m_fades), fadeout_vect)                     # Último Fade-Out
                time_lapse_vector = np.concatenate((time_lapse_vector, chunk_fade, chunk, chunk_final)) # Último Chunk
        else:                                                                                       #### Segmentos intermedios.
            chunk_fadeout     = np.multiply(in_sig.read(m_fades), fadeout_vect)                     #
            in_sig.read(m_desc)                                                                     #
            chunk_fadein      = np.multiply(in_sig.read(m_fades), fadein_vect)                      #
            chunk_fade        = chunk_fadein + chunk_fadeout                                        #
            chunk             = in_sig.read(m_segment - 2 * m_fades)                                #
            time_lapse_vector = np.concatenate((time_lapse_vector, chunk_fade, chunk))              #
        progress_per_chunk = 1.0/n_chunks                                                           # Progreso por cada segmento.
        cont              += progress_per_chunk                                                     # Conteo del progreso.
        percent_progress   = cont/len(filez) * 100                                                  # Porcentaje de progreso.
        sys.stdout.write("\rProgreso: "+str(percent_progress)+'%. ')                                # Barra de progreso.
        sys.stdout.flush()
    return time_lapse_vector, chunk_fadeout, cont


def stereoToMono(in_sig):
    newaudiodata = []

    for i in range(len(in_sig)):
        d = (float(in_sig[i][0]) + float(in_sig[i][1]))/2
        newaudiodata.append(d)

    return np.array(newaudiodata, dtype='int16')

def check_stereo(in_sig):
    channels=in_sig.channels
    if channels==2:
        stereo=True
    else : 
        stereo=False
    return stereo
