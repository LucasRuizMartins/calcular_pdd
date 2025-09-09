import pandas as pd

class PDDService:
    def __init__(self, path_estoque=None):
        self.path_estoque = path_estoque
        self.df_estoque = None
        self.estoque_agrupado = None
        self.df_final = None
        self.data_ref = None 

    def iniciar_pdd(self,com_vagao = True):
        self.df_estoque =  pd.read_csv(self.path_estoque, 
                          encoding='ISO-8859-1',
                          on_bad_lines='skip', 
                          delimiter=';',
                          decimal=',', 
                          thousands='.',  
                          low_memory=False)
        
        self.data_ref = self.df_estoque["DATA_REFERENCIA"].values[0]
        if com_vagao : 
            self.executar_pdd_com_vagao()
        else:
            self.executar_pdd_sem_vagao()

    def executar_pdd_com_vagao(self):
        self.data_ref = self.recuperar_data_referencia(self.df_estoque)
        self.df_estoque = self.filtrar_colunas_estoque(self.df_estoque)        
        self.estoque_agrupado = self.agrupar_estoque(self.df_estoque) 
        self.estoque_agrupado = self.acrescentar_faixa_pdd(self.estoque_agrupado)
        print(self.estoque_agrupado)
        self.df_final = self.agrupar_df_final(self.estoque_agrupado)
        self.df_final = self.gerar_percentual_pdd(self.df_final)
        self.df_final = self.ordenar_pdd(self.df_final)
        self.df_final = self.multiplicar_pdd(self.df_final)
        print(self.df_final)

    def executar_pdd_sem_vagao(self):
        self.data_ref = self.recuperar_data_referencia(self.df_estoque)
        self.df_estoque = self.filtrar_colunas_estoque(self.df_estoque)        
        self.estoque_agrupado = self.acrescentar_faixa_pdd(self.df_estoque)        
        self.df_final = self.agrupar_df_final(self.estoque_agrupado)
        self.df_final = self.gerar_percentual_pdd(self.df_final)
        self.df_final = self.ordenar_pdd(self.df_final)
        self.df_final = self.multiplicar_pdd(self.df_final)

    def categorizar_prazo_atual(self,prazo):
        if prazo <= 0 and prazo >= -30:
            return "0~30"
        elif prazo < -30 and prazo >= -60:
            return "31~60"
        elif prazo < -60 and prazo >= -90:
            return "61~90"
        elif prazo < -90 and prazo >= -120:
            return "91~120"
        elif prazo < -120 and prazo >= -150:
            return "121~150"
        elif prazo < -160 and prazo >= -180:
            return "151~180"
        elif prazo < -180 and prazo >= -210:
            return "181~210"
        elif prazo < -210 and prazo >= -240:
            return "211~240"
        elif prazo < -240 and prazo >= -270:
            return "241~270"
        elif prazo < -270 and prazo >= -300:
            return "271~300"
        elif prazo < -300 and prazo >= -330:
            return "301~330"
        elif prazo < -330 and prazo >= -360:
            return "331~360"
        elif prazo < -360:
            return "+360"
        else:
            return "A vencer"

    def percentual_faixa_pdd(self,faixa):
        if faixa == "0~30":
            return 0.0      # 0%
        elif faixa == "31~60":
            return 0.19    # 14.13%
        elif faixa == "61~90": 
            return 0.21 
        elif faixa == "91~120": 
            return 0.3375  
        elif faixa == "121~150":
            return 0.22    
        elif faixa == "151~180":
            return 0.24   
        elif faixa == "181~210":
            return 0.26   
        elif faixa == "211~240":
            return 0.31   
        elif faixa == "241~270":
            return 0.38   
        elif faixa == "271~300":
            return 0.50
        elif faixa == "301~330":
            return 0.78
        elif faixa == "331~360":
            return 0.78
        elif faixa == "+360":
            return 1
        else:
            return 0.0       

    def recuperar_data_referencia(self,df):
        return df["DATA_REFERENCIA"].values[0]

    def filtrar_colunas_estoque(self,df):
        return df[["DOC_SACADO","SEU_NUMERO","FAIXA_PDD","NU_DOCUMENTO","PRAZO_ATUAL","VALOR_AQUISICAO","VALOR_NOMINAL","VALOR_PRESENTE","DATA_REFERENCIA"]]

    def agrupar_estoque(self,df):
        estoque_agrupado = df.groupby('DOC_SACADO').agg({
        'VALOR_AQUISICAO': 'sum',
        'VALOR_NOMINAL': 'sum',
        'VALOR_PRESENTE': 'sum',
        'PRAZO_ATUAL': 'min',
        'DATA_REFERENCIA': 'first',
        }).reset_index()
        return estoque_agrupado


    def acrescentar_faixa_pdd(self,df):
        df['FAIXA_PDD'] = df['PRAZO_ATUAL'].apply(self.categorizar_prazo_atual)
        return df

    def agrupar_df_final(self,df):    
        df[~df.FAIXA_PDD.str.contains('A vencer')]
        df = df.groupby('FAIXA_PDD').agg({
        'VALOR_AQUISICAO': 'sum',
        'VALOR_NOMINAL': 'sum',
        'VALOR_PRESENTE': 'sum',
        }).reset_index()
        return df


    def gerar_percentual_pdd(self,df):
        df['% PDD'] = df['FAIXA_PDD'].apply(self.percentual_faixa_pdd)
        return df


    def ordenar_pdd(self,df):
        ordem_faixapdd = ["A vencer", "0~30", "31~60", "61~90","91~120","121~150","151~180","181~210","211~240","241~270","271~300","301~330","331~360","+360"]
        df["FAIXA_PDD"] = pd.Categorical(
            df["FAIXA_PDD"],
            categories=ordem_faixapdd,
            ordered=True
        ) 
        df = df.sort_values("FAIXA_PDD")
        df = df.reset_index(drop=True)
        return df

    def multiplicar_pdd(self,df):
        df["PDD POR FAIXA"] = df["VALOR_PRESENTE"] * df["% PDD"]
        return df
        
    def reordenar_colunas(self,df):
        df
        df = df[[col for col in df.columns if col != 'DATA_REFERENCIA'] + ['DATA_REFERENCIA']]
        return df


    def gerar_linha_total(self,df_final):
        data = df_final[["DATA_REFERENCIA"]].iloc[0,0]        
        linha_total = {
            'FAIXA_PDD': 'Total',
            'VALOR_AQUISICAO': df_final['VALOR_AQUISICAO'].sum(),
            'VALOR_NOMINAL':df_final['VALOR_NOMINAL'].sum(),
            'VALOR_PRESENTE': df_final['VALOR_PRESENTE'].sum(),
            '% PDD': np.nan,
            'PDD POR FAIXA': df_final['PDD POR FAIXA'].sum(),
            'DATA_REFERENCIA': data
        }        
        df_final = pd.concat([df_final, pd.DataFrame([linha_total])], ignore_index=True)
        return df_final