import pandas as pd
import requests
from bs4 import BeautifulSoup
import time 
from urllib.parse import urljoin
dados=[]
urls_categorias = [
    "https://testingurl.dev/scraping/ecommerce/category/laptops",
    "https://testingurl.dev/scraping/ecommerce/category/phones",
    "https://testingurl.dev/scraping/ecommerce/category/cameras",
    "https://testingurl.dev/scraping/ecommerce/category/headphones"
]

def carregar_pagina(url, tentativas=3, espera=5):
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, timeout=10)
            resposta.raise_for_status()
            return resposta.text
        except requests.exceptions.RequestException as erro:
            print(f"Tentativa {tentativa} falhou: {erro}")
            if tentativa == tentativas:
                raise  # depois de esgotar as tentativas, aí sim deixa o erro estourar
            time.sleep(espera)  # espera antes de tentar de novo
        return url 

for url in urls_categorias:
    pagina = carregar_pagina(url)
    soup = BeautifulSoup(pagina, "html.parser")
    # extrair os produtos dessa categoria
    categorias = soup.find_all('main', class_='site-main')
    for categoria in categorias:
        if categoria:
            categoria_titulo = categoria.find("h1")
            nome_categoria=(categoria_titulo.get_text(strip=True)
        if categoria_titulo else None)

    produtos = soup.find_all("a", class_='card')

    for produto in produtos:
        url_relativa=produto.get('href')
        url_produto = urljoin(url, url_relativa) if url_relativa else None
        nome_do_produto = produto.find("h3")
        preco = produto.find("p")
        preco_texto = preco.find(
        string=True, recursive=False).strip()
        avaliacao= produto.find('span', class_='stars')
        pagina_produto = carregar_pagina(url_produto)
        soup_produto = BeautifulSoup(pagina_produto, "html.parser")
        estoque = soup_produto.find("p", attrs={"data-field": "stock"})
        quantidade_estoque = (
        estoque.get("data-value") if estoque else None)
        dados.append({
        'categoria': nome_categoria,
        "nome do produto": nome_do_produto.get_text(strip=True)
        if nome_do_produto else None,
        "preço": preco.get_text (strip=True)
        if preco else None,
        'avaliação': avaliacao.get('aria-label')
        if avaliacao else None,
        'estoque': quantidade_estoque,
        'url': url_produto})
df= pd.DataFrame(dados)
def limpar_dados(df):
    df["preço"] = (df["preço"].str.replace("$", "", regex=False).replace('.',"", regex=False))
    df["preço"] = pd.to_numeric(df["preço"], errors="coerce")
    df['estoque']=pd.to_numeric(df['estoque'], errors='coerce')
    df = df.drop_duplicates()
    print("Valores ausentes:")
    print(df.isnull().sum())
    print("\nTipos de dados:")
    print(df.dtypes)
    return df
df = limpar_dados(df)
def analise(df):
    total= df['nome do produto'].count()
    media_precos=df['preço'].mean()
    maior_preco= df['preço'].max()
    menor_preco=df['preço'].min()
    prod_categoria= df.groupby('nome do produto')['categoria'].sum()
    prod_disponiveis=df.groupby('nome do produto')['estoque'].sum()
    preco_categoria=df.groupby('categoria')['preço'].mean()
    return total, media_precos,maior_preco, menor_preco, prod_categoria, prod_disponiveis, preco_categoria
total, media_precos,maior_preco, menor_preco, prod_categoria, prod_disponiveis, preco_categoria= analise(df)
def new_func(variavel, writer):
    df_categoria=pd.DataFrame(variavel.to_list())
    df_categoria.to_excel(
        writer, sheet_name='produtos por cada categoria', index=False
    )
    with pd.ExcelWriter(
    'relatorio_loja.xlsx', engine="openpyxl")as writer:
        df.to_excel( writer,sheet_name="Catalogo",index=False)

    # Resumo geral
    df_resumo = pd.DataFrame({
        "Métrica": [
            "Total de produtos",
            "Preço médio",
            "Maior preço",
            "Menor preço",
            "Estoque total",
            "Estoque médio"],
        "Valor": [
            total,
            media_precos,
            maior_preco,
            menor_preco,
        ]})
    df_resumo.to_excel(
        writer,
        sheet_name="Resumo",
        index=False
    )
# produtos por categoria
    df_categoria = (
        prod_categoria
        .reset_index())
    df_categoria.columns = [
        "Categoria",
        "Quantidade de produtos"]
    df_categoria.to_excel(
        writer,
        sheet_name="Categorias",
        index=False)

