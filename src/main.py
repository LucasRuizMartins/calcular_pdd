import flet as ft
import pandas as pd
from services.pdd_service import PDDService
import os
 

def dataframe_para_datatable(df: pd.DataFrame) -> ft.DataTable:
    columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]
    rows = [
        ft.DataRow(
            cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
        )
        for row in df.values.tolist()
    ]
    return ft.DataTable(columns=columns, rows=rows)



def main(page: ft.Page):
    user_profile = os.environ['USERPROFILE']
    path_estoque =  user_profile + r"\Carmel Capital\TECNOLOGIA - Geral\BUSINESS INTELLIGENCE\BASE PDD\RESIDENCE\estoque.csv"
    path_movimento = user_profile + r"\Carmel Capital\TECNOLOGIA - Geral\BUSINESS INTELLIGENCE\BASE PDD\RESIDENCE\movimento.csv"
    # Configuração da página
    page.title = "Calculadora PDD"
    page.window_width = 800
    page.window_height = 600

    pdd = PDDService(path_estoque,path_movimento)

    pdd.iniciar_pdd()

    # Elementos da interface
    titulo = ft.Text("Calculadora de Provisão para Devedores Duvidosos (PDD)", size=24)
    input_file = ft.FilePicker()
    btn_carregar = ft.ElevatedButton("Carregar Planilha", on_click=lambda _: input_file.pick_files())
    tabela_df_final = dataframe_para_datatable(pdd.df_final)
    #print(pdd.df_final)
    
    # Layout
    page.add(
            ft.Column([
                titulo,
                ft.Text(f'Data do arquivo: {pdd.data_ref}'),
                ft.Row([btn_carregar]),
                tabela_df_final  # Aqui está a exibição do DataFrame
            ])
        )

    # Lógica para processar arquivos
    def processar_arquivo(e):
        if input_file.result.files:
            caminho = input_file.result.files[0].path
            df = pd.read_excel(caminho)
            # Adicione sua lógica de cálculo aqui
            page.add(ft.Text(f"Arquivo processado: {caminho}"))
    
    input_file.on_result = processar_arquivo

ft.app(target=main)