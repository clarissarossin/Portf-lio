import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
pasta = Path(__file__).parent
df = pd.read_excel(pasta / 'base_vendas_projeto_2.xlsx')
print(df.head())
print("Informações básicas iniciais:")
df.info()
from funcoes_coringas import  limpar_colunas
dados_limpos=limpar_colunas(df)
print (dados_limpos)

def limpar_dados(df):
    df = df.drop_duplicates()
    print(df.isnull().sum())
    print(df.dtypes)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['mes'] = df['data'].dt.to_period('M').astype(str)
    df['preco_unitario'] = df['preco_unitario'].astype(str).str.replace(',', '.', regex=False)   
    df['preco_unitario'] = pd.to_numeric(df['preco_unitario'], errors='coerce')
    df['preco_unitario'] = df['preco_unitario'].fillna(df.groupby('produto')['preco_unitario'].transform('mean'))    
    df['quantidade'] = df['quantidade'].fillna(df.groupby('produto')['quantidade'].transform('mean')).round()
    df['faturamento'] = df['quantidade'] * df['preco_unitario']
    return df
df=limpar_dados(df)

def analisar_dados(df):
    ## Visão geral:
    fat_total = df["faturamento"].sum()
    ticket_medio = df["faturamento"].mean()
    maior_venda = df["faturamento"].max()
    menor_faturamento_positivo = df[df['faturamento'] > 0]['faturamento'].min()
    total_de_vendas= len(df)
    ## Produtos:
    fat_produto= df.groupby('produto')['faturamento'].sum()
    total_de_produtos=df['quantidade'].sum()
    maior_venda_por_produto = df.groupby('produto')['faturamento'].max()
    mais_unidades_vendidas= df.groupby('produto')['quantidade'].sum().idxmax()
    categoria_com_mais_vendas= df.groupby('categoria')['faturamento'].sum().idxmax()
    ## Cidades:
    fat_max_cidade= df.groupby('cidade')['faturamento'].max()
    vendas_por_cidade = df['cidade'].value_counts()    
    ## Vendedores:
    venda_maior_por_vendedor= df.groupby('vendedor')['faturamento'].max()
    faturamento_por_vendedor= df.groupby('vendedor')['faturamento'].sum()

    return fat_total, ticket_medio, maior_venda,fat_produto, fat_max_cidade, total_de_vendas, total_de_produtos,maior_venda_por_produto, mais_unidades_vendidas,categoria_com_mais_vendas, venda_maior_por_vendedor, faturamento_por_vendedor, vendas_por_cidade, menor_faturamento_positivo

## Mensal:
fat_mensal= df.groupby('mes')['faturamento'].sum()
maior_fat_mensal= df.groupby('mes')['faturamento'].max()
evolucao_mensal= df.groupby('mes')['faturamento'].sum().pct_change()

fat_total, ticket_medio, maior_venda, fat_produto, fat_max_cidade, total_de_vendas, total_de_produtos,maior_venda_por_produto, mais_unidades_vendidas,categoria_com_mais_vendas, venda_maior_por_vendedor, faturamento_por_vendedor, vendas_por_cidade, menor_faturamento_positivo= analisar_dados(df)

relatorio_geral={
    "Faturamento Total": fat_total,
    "Ticket Médio": ticket_medio,
    "Maior Venda": maior_venda,
    "Menor Venda": menor_faturamento_positivo,
    "Total de Vendas": total_de_vendas,
    "Total de Produtos": total_de_produtos,
    "Mais Unidades Vendidas": mais_unidades_vendidas,
    "Categoria com Mais Vendas": categoria_com_mais_vendas
}
relatorio_de_produtos={
    'Faturamento por produto': fat_produto,
    'Maior venda por produto': maior_venda_por_produto,
    'Total de produtos vendidos': total_de_produtos,
    'Produto mais vendido': mais_unidades_vendidas,
}
relatorio_mensal={
    'Faturamento Mensal': fat_mensal,
    'Maior Faturamento Mensal': maior_fat_mensal,
    'Evolução Mensal das vendas': evolucao_mensal
}
relatorio_cidades={
    'Cidade com maior faturamento': fat_max_cidade,
    'Vendas por cidade': vendas_por_cidade
}
relatorio_vendedores={
    'Faturamento por vendedor': faturamento_por_vendedor,
    'Venda maior por vendedor': venda_maior_por_vendedor
}

from matplotlib.ticker import FuncFormatter


def formatar_reais(valor, _):
    return f'{valor:,.0f}'.replace(',', '.')


def grafico_barras(df, coluna, titulo, arquivo, top=10):
    """Barras horizontais ordenadas, mostrando só os 'top' maiores."""
    fat = (df.groupby(coluna)['faturamento'].sum()
             .sort_values(ascending=False).head(top).sort_values())
    ax = fat.plot(kind='barh', figsize=(10, 6))
    ax.xaxis.set_major_formatter(FuncFormatter(formatar_reais))
    ax.set_title(titulo)
    ax.set_xlabel('faturamento (R$)')
    ax.set_ylabel('')
    plt.tight_layout()
    plt.savefig(pasta / arquivo, dpi=150)
    plt.show()
    plt.close()
def gerar_grafico_produto(df):
    grafico_barras(df, 'produto', 'Top 10 produtos por faturamento', 'grafico_produto.png')
def gerar_grafico_cidade(df):
    grafico_barras(df, 'cidade', 'Top 10 cidades por faturamento', 'grafico_cidade.png')
def gerar_grafico_categoria(df):
    grafico_barras(df, 'categoria', 'Faturamento por categoria', 'grafico_categoria.png')
def gerar_grafico_evolucao_mensal(df):
    fat = df.groupby('mes')['faturamento'].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(fat.index, fat.values, marker='o')
    passo = max(1, len(fat) // 12)  # mostra no máximo ~12 meses no eixo
    ax.set_xticks(range(0, len(fat), passo))
    ax.set_xticklabels(fat.index[::passo], rotation=45, ha='right')
    ax.yaxis.set_major_formatter(FuncFormatter(formatar_reais))
    ax.set_title('Faturamento mensal')
    ax.set_xlabel('mês')
    ax.set_ylabel('faturamento (R$)')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(pasta / 'grafico_evolucao_mensal.png', dpi=150)
    plt.show()
    plt.close(fig)
gerar_grafico_produto(df)
gerar_grafico_cidade(df)
gerar_grafico_categoria(df)
gerar_grafico_evolucao_mensal(df)

def escrever_relatorio(writer, nome_aba, relatorio):
    linha = 0
    for titulo, valor in relatorio.items():
        if isinstance(valor, pd.Series):
            tabela = valor.rename(titulo).to_frame()
        else:
            tabela = pd.DataFrame({titulo: [valor]})
        tabela.to_excel(writer, sheet_name=nome_aba, startrow=linha)
        linha += len(tabela) + 3
with pd.ExcelWriter(pasta / "relatorio_geral.xlsx") as writer:
    pd.DataFrame([relatorio_geral]).to_excel(writer, sheet_name='Relatório Geral', index=False)
escrever_relatorio(writer, 'Relatório de Produtos', relatorio_de_produtos)
escrever_relatorio(writer, 'Relatório Mensal', relatorio_mensal)
escrever_relatorio(writer, 'Relatório de Cidades', relatorio_cidades)
escrever_relatorio(writer, 'Relatório de Vendedores', relatorio_vendedores)

class min:
    """Utility container that keeps track of the smallest value seen."""

    def __init__(self, values=None):
        self.values = [] if values is None else list(values)

    def add(self, value):
        """Add a new value and keep the collection usable."""
        self.values.append(value)
        return self

    def add_many(self, values):
        """Add several values at once."""
        self.values.extend(values)
        return self

    def get_min(self):
        """Return the minimum value currently stored."""
        if not self.values:
            raise ValueError("No values available to compute the minimum.")
        return min(self.values)

    def __len__(self):
        return len(self.values)

    def __bool__(self):
        return bool(self.values)

    def __iter__(self):
        return iter(self.values)

    def __repr__(self):
        return f"min({self.values!r})"


# Example usage:
if __name__ == "__main__":
    tracker = min([9, 4, 7, 2, 8])
    tracker.add(1)
    print(tracker.get_min())
    print(repr(tracker))
