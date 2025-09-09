import flet as ft
import pandas as pd
from services.pdd_service import PDDService


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
    page.title = "Calculadora PDD"
    page.window_width = 800
    page.window_height = 600

    # Variáveis para armazenar os paths escolhidos
    path_estoque = None
    

    # Componentes de escolha de arquivos
    picker_estoque = ft.FilePicker()
    

    page.overlay.extend([picker_estoque])

    # Campos para exibir os caminhos escolhidos
    txt_estoque = ft.Text("Arquivo de estoque: (não selecionado)")
    

    def selecionar_estoque(e):
        nonlocal path_estoque
        if picker_estoque.result and picker_estoque.result.files:
            path_estoque = picker_estoque.result.files[0].path
            txt_estoque.value = f"Arquivo de estoque: {path_estoque}"
            page.update()

   


    picker_estoque.on_result = selecionar_estoque


    # Função para processar os arquivos
    def processar_pdd_com_vagao(e):
        if path_estoque:
            pdd = PDDService(path_estoque)
            pdd.iniciar_pdd()
            tabela_df_final = dataframe_para_datatable(pdd.df_final)
            page.add(
                ft.Text(f"Data do arquivo: {pdd.data_ref}"),
                tabela_df_final
            )
        else:
            page.add(ft.Text("⚠️ Selecione os dois arquivos antes de processar."))

    def processar_pdd_sem_vagao(e):
        if path_estoque:
            pdd = PDDService(path_estoque)
            pdd.iniciar_pdd(False)
            tabela_df_final = dataframe_para_datatable(pdd.df_final)
            page.add(
                ft.Text(f"Data do arquivo: {pdd.data_ref}"),
                tabela_df_final
            )
        else:
            page.add(ft.Text("⚠️ Selecione os dois arquivos antes de processar."))

    # Botões para seleção de arquivos e processamento
    btn_sel_estoque = ft.ElevatedButton("Selecionar Estoque", on_click=lambda _: picker_estoque.pick_files())
    btn_processar = ft.ElevatedButton("Processar PDD com Vagao", on_click=processar_pdd_com_vagao)
    btn_processar_sem_vagao = ft.ElevatedButton("Processar PDD Sem Vagao", on_click=processar_pdd_sem_vagao)

    # Layout inicial
    page.add(
        ft.Column([
            ft.Text("Calculadora de Provisão para Devedores Duvidosos (PDD)", size=24),
            txt_estoque,
            btn_sel_estoque,
            btn_processar,
            btn_processar_sem_vagao
            
        ])
    )


ft.app(target=main)
