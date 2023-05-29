# importando bibliotecas
import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm, colors
from PIL import Image

# determinando parâmetros comuns a todos os plots
plt.style.use('seaborn')
norm = mpl.colors.Normalize(vmin = 2010, vmax = 2060)

# funções auxiliares
def p_morte(tabua, coluna, idade, t): # t pra gente é 5, só fiz mais generalizado, vai que pode ser útil

    p = 0 # probabilidade de morrer na faixa de idade [x, x + t]
    for i in range(t): # 0 a t - 1 inclusive
        p_i = tabua[coluna][idade + i] # probabilidade de morrer tendo idade + i
        for j in range(i): # para cada j indo até i - 1
            q_j = 1 - tabua[coluna][idade + j] # probabilidades de NÃO morrer indo até idade + i - 1
            p_i *= q_j
        p += p_i
    return p

def abrevia_tabua(tabua_desabreviada):

    tabua_abreviada = pd.DataFrame({}, columns = tabua_desabreviada.columns) # df zerado, tendo só os nomes das colunas  
    for idade in tabua_desabreviada['Idade']: # pra cada idade começando em 20 e subindo
        if idade % 5 == 0: # se a idade é um múltiplo de 5, vai ter que calcular usando aquela recursão
            nova_linha = {'Idade': [idade]} # cria um df pra nova linha
            for coluna in tabua_desabreviada.columns[1:]: # pra cada coluna fixada, excluindo-se a de idades
                nova_linha[coluna] = [p_morte(tabua_desabreviada, coluna, idade, 5)]
            nova_linha = pd.DataFrame(nova_linha)
            tabua_abreviada = pd.concat([tabua_abreviada, nova_linha], ignore_index = True)
    return tabua_abreviada

st.markdown('# Comparação da tábua BR-EMS 2021 com a projeção do IBGE 2010-2060 :bar_chart: \
\n\n --- \n\n Esse Dashboard foi construído com o intuito de mostrar os resultados do estudo de comparação da expectativa de \
vida e da probabilidade de morte da tábua BR-EMS (Experiência do Mercado Segurador Brasileiro) de 2021 com as projeções \
do IBGE para os anos de 2010 a 2060.')

expander = st.expander('Mais informação')
expander.write('A motivação por trás da comparação entre as tábuas é que conjuntos de valores como as probabilidades \
de morte para cada idade são um indicativo indireto da qualidade de vida da população em estudo. Desse modo, nosso objetivo \
ao comparar as duas tábuas (\*sic) é, dentre outros objetivos futuros, estimar **quando** a qualidade de vida de uma população \
em geral vai se comparar com a qualidade de vida da parcela segurada da população brasileira.')

st.markdown('---')

image = Image.open('Logo_LabMA.png')
st.sidebar.image(image, caption = 'Lab de Matemática Aplicada', width = 120)

zoom = st.sidebar.selectbox('Selecione um nível de detalhe 🔍', ['-', 'Brasil inteiro', 'Por macrorregião', 'Por estado'])

if zoom == '-':
    st.sidebar.success('Escolha uma das opções acima.')

if zoom == 'Brasil inteiro':
    sheet_name = 'Brasil'

elif zoom == 'Por macrorregião':
    # st.map()
    regiao = st.sidebar.selectbox('Selecione uma macrorregião 📍', ['-', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'])
    sheet_name = regiao

elif zoom == 'Por estado':
    # st.map()
    estado = st.sidebar.selectbox('Selecione um estado 📍', ['-', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
                                                          'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'])
    sheet_name = estado

if zoom != '-' and sheet_name != '-':
    df = pd.read_excel(f'Tabuas_Mortalidade_2010_2060_{sheet_name}.xlsx')
    df = df.query('20 <= Idade < 85')

    metrica = st.sidebar.selectbox('Selecione a métrica 📏', ['-', 'ex (expectativa de sobrevida)', 'qx (probabilidade de morte)'])

    # depois de selecionar o 'zoom' e a métrica, o usuário já deve poder ver os resultados da seleção
    if metrica == 'ex (expectativa de sobrevida)':
        # expectativa de vida da br-ems:
        br_ems_2021_ex = pd.read_excel('br_ems_2021_ex.xlsx').query('20 <= Idade < 80')

        # tabua homem ibge ex
        ex_homem = pd.DataFrame(df.query("Sexo == 'h'")[['Idade', 'Ano', 'ex']], dtype = 'float64')
        ex_homem_pivot = ex_homem.pivot_table(index = 'Idade', columns = 'Ano', values = 'ex')

        # tabua mulher ibge ex
        ex_mulher = pd.DataFrame(df.query("Sexo == 'm'")[['Idade', 'Ano', 'ex']], dtype = 'float64')
        ex_mulher_pivot = ex_mulher.pivot_table(index = 'Idade', columns = 'Ano', values = 'ex')

        # criando a figura
        fig, ax = plt.subplots(1, 2, sharey = True, figsize = [16, 6])
        colormap = sns.color_palette('plasma', 51)

        for color, ano in zip(colormap, ex_homem_pivot.columns):
            ax[0].plot(ex_homem_pivot.index, ex_homem_pivot[ano], lw = 0.5, color = color)

        ax[0].plot(br_ems_2021_ex['Idade'][:93], br_ems_2021_ex['BR-EMSmt-v.2021-m'][:93],
                   color = 'k', linestyle = 'dotted', label = 'BR-EMS 2021')
        ax[0].legend()

        for color, ano in zip(colormap, ex_mulher_pivot.columns):
            ax[1].plot(ex_mulher_pivot.index, ex_mulher_pivot[ano], lw = 0.5, color = color)

        ax[1].plot(br_ems_2021_ex['Idade'][:93], br_ems_2021_ex['BR-EMSmt-v.2021-f'][:93],
                   color = 'k', linestyle = 'dotted', label = 'BR-EMS 2021')
        ax[1].legend()

        fig.suptitle('Comparação BR-EMS e Projeção do IBGE por sexo')
        ax[0].set_title('População masculina')
        ax[0].set_xlabel('Idade')
        ax[0].set_ylabel('Expectativa de sobrevida')
        ax[1].set_title('População feminina')
        ax[1].set_xlabel('Idade')
        ax[1].set_ylabel('Expectativa de sobrevida')
        fig.colorbar(mpl.cm.ScalarMappable(norm = norm, cmap = 'plasma'))

        st.pyplot(fig)
        st.button('Download ⬇️(Not working yet)')

        options = st.sidebar.multiselect('Mostrar cabeçalho dos datasets?', ['Projeção do IBGE', 'ex BREMS masculino', 'ex BREMS feminino'])
        if 'Projeção do IBGE' in options:
            st.write('Tábuas projetadas do IBGE (população geral)', df.head())
        if 'ex BREMS masculino' in options:
            st.write('ex (expectativa de sobrevida) da população masculina segurada', ex_homem_pivot.head())
        if 'ex BREMS feminino' in options:
            st.write('ex (expectativa de sobrevida) da população feminina segurada', ex_mulher_pivot.head())

    elif metrica == 'qx (probabilidade de morte)':
        # resultado após abreviar a nossa tábua:
        br_ems_2021_qx = pd.read_excel('br_ems_2021_qx.xlsx')
        br_ems_2021_qx = br_ems_2021_qx.query('20 <= Idade < 80')
        br_ems_2021_qx_abreviada = abrevia_tabua(br_ems_2021_qx)

        # lendo as tábuas do IBGE para comparar com a nossa:
        # homem
        nqx_homem = df.query('20 <= Idade < 80 & Sexo == "h"')[['Ano', 'Idade', 'nqx']] # 80 pra cima tá descartado
        nqx_homem_pivot = nqx_homem.pivot_table(index = 'Idade', columns = 'Ano', values = 'nqx')

        # mulher
        nqx_mulher = df.query('20 <= Idade < 80 & Sexo == "m"')[['Ano', 'Idade', 'nqx']] # 80 pra cima tá descartado
        nqx_mulher_pivot = nqx_mulher.pivot_table(index = 'Idade', columns = 'Ano', values = 'nqx')

        # plotando os resultados:

        fig, ax = plt.subplots(1, 2, sharey = True, figsize = [16, 6])

        colormap = sns.color_palette('plasma', 51)

        for color, ano in zip(colormap, nqx_homem_pivot.columns):
            ax[0].semilogy(nqx_homem_pivot.index, nqx_homem_pivot[ano], lw = 0.5, color = color)

        ax[0].semilogy(br_ems_2021_qx_abreviada['Idade'], br_ems_2021_qx_abreviada['BR-EMSmt-v.2021-m'],
                       linestyle = 'dotted', label = 'MOR')
        ax[0].semilogy(br_ems_2021_qx_abreviada['Idade'], br_ems_2021_qx_abreviada['BR-EMSsb-v.2021-m'],
                       linestyle = 'dotted', label = 'SOB')
        ax[0].legend()

        for color, ano in zip(colormap, nqx_mulher_pivot.columns):
            ax[1].semilogy(nqx_mulher_pivot.index, nqx_mulher_pivot[ano], lw = 0.5, color = color)

        ax[1].semilogy(br_ems_2021_qx_abreviada['Idade'], br_ems_2021_qx_abreviada['BR-EMSmt-v.2021-f'],
                       linestyle = 'dotted', label = 'MOR')
        ax[1].semilogy(br_ems_2021_qx_abreviada['Idade'], br_ems_2021_qx_abreviada['BR-EMSsb-v.2021-f'],
                       linestyle = 'dotted', label = 'SOB')
        ax[1].legend()

        fig.suptitle(f'Comparação qx da BR-EMS 2021 e Projeção do IBGE - {sheet_name}')
        ax[0].set_title('Masculino')
        ax[0].set_xlabel('Idade')
        ax[0].set_ylabel('qx')
        ax[1].set_title('Feminino')
        ax[1].set_xlabel('Idade')
        fig.colorbar(mpl.cm.ScalarMappable(norm = norm, cmap = 'plasma'))

        st.pyplot(fig)
        st.button('Download ⬇️(Not working yet)')

        options = st.sidebar.multiselect('Mostrar cabeçalho dos datasets?', ['Projeção do IBGE', 'qx BREMS masculino', 'qx BREMS feminino'])
        if 'Projeção do IBGE' in options:
            st.write('Tábuas projetadas do IBGE (população geral)', df.head())
        if 'qx BREMS masculino' in options:
            st.write('qx (probabilidade de morte) da população masculina segurada', qx_homem_pivot.head())
        if 'qx BREMS feminino' in options:
            st.write('qx (probabilidade de morte) da população feminina segurada', qx_mulher_pivot.head())

    else:
        st.sidebar.success('Escolha uma das opções acima.')

st.markdown('---')

st.code('# TODO: \n# Adicionar mapa com interatividade * \n# Ajustar botão de download de gráfico * \n# Interatividade do plot ?* \
\n\n# Próximos passos? \n# Sugestões?')

st.caption('Desenvolvido por: Gabriel Bastianello, guiado por Rodrigo Lima Peregrino, em um estudo para o Laboratório de Matemática Aplicada da UFRJ')
