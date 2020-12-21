from .charges import *
import pandas as pd
from datetime import date

class ChiffreAffaire():
    
    
    def __init__(self,dicCharges):
        self.__dicCharges = dicCharges.get_raw_charges()
        self.__delete_ach_lines()
        self.__ca_mois = pd.DataFrame()
        self.__ca_annee = pd.DataFrame() 
        

    
    def __delete_ach_lines(self):
        ''' Elimine toutes les lignes d'achats pour ne garder que les ventes '''
        for index,value in self.__dicCharges['Journal'].iteritems():
            if value != 'VEN':
                self.__dicCharges = self.__dicCharges.drop(index=index)

    

    def calcul_ca_mois(self,mois,annee):
        ''' Calcul le chiffre d'affaire du mois de l'année donné en argument '''
        result = 0.0
        for index,row in self.__dicCharges.iterrows():
            date = row['Date']
            if (date.month == mois and date.year == annee):
                print(str(date) + ' / ' + str(row['Crédit']))
                result += row['Crédit']
        
        return result


    
    def calcul_ca_annee(self,annee):
        ''' Calcul le chiffre d'affaire de l'année donnée en argument '''
        today = date.today()
        result = 0.0
        for i in range (1,today.month):
            result += self.calcul_ca_mois(i,today.year)

        return result
