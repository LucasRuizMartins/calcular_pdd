import pandas as pd

class PDDService:
    def __init__(self, path_estoque=None, path_movimento=None):
        self.path_estoque = path_estoque
        self.path_movimento = path_movimento 
        self.df_estoque = None
        self.df_movimento = None
        self.df_final = None
        self.data_ref = None 

    def iniciar_pdd(self):
        self.df_estoque =  pd.read_csv(self.path_estoque, 
                          encoding='ISO-8859-1',
                          on_bad_lines='skip', 
                          delimiter=';',
                          decimal=',', 
                          thousands='.',  
                          low_memory=False)

        self.df_movimento = pd.read_csv(self.path_movimento, 
                                encoding='ISO-8859-1',
                                on_bad_lines='skip', 
                                delimiter=';',
                                decimal=',', 
                                thousands='.',  
                                low_memory=False) 
        
        self.data_ref = self.df_estoque["DATA_REFERENCIA"].values[0]
        self.executar_pdd()

    
    def executar_pdd(self):
        df_estoque = self.filtrar_colunas_estoque(self.df_estoque)
        df_movimento = self.filtrar_movimento(self.df_movimento)
        df_estoque_filtrado = self.atualizar_estoque_por_dados_movimento(df_estoque, df_movimento)
        estoque_agrupado = self.agrupar_estoque(df_estoque_filtrado)
        estoque_agrupado = self.acrescentar_faixa_pdd(estoque_agrupado)
        df_final = self.agrupar_df_final(estoque_agrupado)
        df_final = self.gerar_percentual_pdd(df_final)
        df_final = self.ordenar_pdd(df_final)
        df_final = self.multiplicar_pdd(df_final)
        self.df_final = df_final  # Resultado final


    def categorizar_prazo_atual(self,prazo):
        if prazo <= 0 and prazo >= -5:
            return "0~5"
        elif prazo < -5 and prazo >= -30:
            return "6~30"
        elif prazo < -30 and prazo >= -60:
            return "31~60"
        elif prazo < -60 and prazo >= -90:
            return "61~90"
        elif prazo < -90 and prazo >= -120:
            return "91~120"
        elif prazo < -120:
            return "+120"
        else:
            return "A vencer"

    def percentual_faixa_pdd(self,faixa):
        if faixa == "0~5":
            return 0.0      # 0%
        elif faixa == "6~30":
            return 0.05      # 5%
        elif faixa == "31~60":
            return 0.1413    # 14.13%
        elif faixa == "61~90":
            return 0.3375    # 33.75%
        elif faixa == "91~120":
            return 0.3375    # 33.75%
        elif faixa == "+120":
            return 0.7352    
        else:
            return 0.0     



    def filtrar_colunas_estoque(self,df_estoque):
        return df_estoque[["DOC_SACADO","SEU_NUMERO","NU_DOCUMENTO","PRAZO_ATUAL","VALOR_AQUISICAO","VALOR_NOMINAL","VALOR_PRESENTE"]]

    def filtrar_movimento(self,df_movimento):
        try:
            if all(col in df_movimento.columns for col in ["SEU_NUMERO", "NUMERO_DOCUMENTO"]):
                return df_movimento[["SEU_NUMERO", "NUMERO_DOCUMENTO"]]
            else:
                print("Colunas 'SEU_NUMERO' ou 'NUMERO_DOCUMENTO' não encontradas. Retornando DataFrame vazio.")
                return pd.DataFrame(columns=["SEU_NUMERO", "NUMERO_DOCUMENTO"])
        except Exception as e:
            print(f"Erro ao filtrar movimento: {str(e)}")
            return pd.DataFrame(columns=["SEU_NUMERO", "NUMERO_DOCUMENTO"])
            
    def atualizar_estoque_por_dados_movimento(self,df_estoque,df_movimento):
        return  df_estoque[~df_estoque['NU_DOCUMENTO'].isin(df_movimento['NUMERO_DOCUMENTO'])]

    def agrupar_estoque(self,df):
        estoque_agrupado = df.groupby('DOC_SACADO').agg({
        'VALOR_AQUISICAO': 'sum',
        'VALOR_NOMINAL': 'sum',
        'VALOR_PRESENTE': 'sum',
        'PRAZO_ATUAL': 'min'
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
        ordem_faixapdd = ["A vencer", "0~5", "6~30", "31~60", "61~90", "91~120","+120"]
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
        