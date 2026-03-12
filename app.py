
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
from fpdf import FPDF
import os

# 1. CONFIGURAÇÃO DA PÁGINA 
st.set_page_config(page_title="Luna AI Analytics", page_icon="🌙", layout="centered")

# 2. GERENCIAMENTO SEGURO DA CHAVE (SISTEMA DE COFRE) 
chave = st.secrets.get("GROQ_API_KEY", "")

if not chave:
    st.warning("⚠️ Configuração necessária: A chave da API não foi encontrada nos Secrets.")
    client = None
else:
    client = Groq(api_key=chave.strip())

# 3. INTERFACE DO USUÁRIO
st.title("🌙 Luna AI - Relatórios Inteligentes")
st.markdown("""
    Transforme dados de vendas em relatórios estratégicos com Inteligência Artificial.
    *Desenvolvido por Andrea - Back-End Developer.*
""")

st.divider()

# 4. ENTRADA DE DADOS 
st.subheader("📥 Passo 1: Carregar Dados")
metodo = st.radio(
    "Escolha como deseja testar a ferramenta:",
    ("Usar dados de exemplo (Modo Demo)", "Subir minha própria planilha (CSV)"),
    horizontal=True
)

df = None

if metodo == "Usar dados de exemplo (Modo Demo)":
    # Dados fictícios para teste
    dados_demo = {
        'produto': ['SaaS Pro', 'Consultoria', 'Licença Anual', 'Suporte VIP', 'Mentoria Tech'],
        'valor': [15000.00, 8500.00, 22000.00, 5000.00, 12500.00]
    }
    df = pd.DataFrame(dados_demo)
    st.info("💡 Você está usando dados de demonstração. Clique no botão abaixo para gerar a análise.")
else:
    arquivo = st.file_uploader("📂 Suba seu arquivo CSV", type="csv")
    if arquivo:
        try:
            df = pd.read_csv(arquivo, encoding='latin-1')
        except:
            df = pd.read_csv(arquivo, encoding='utf-8')

# 5. PROCESSAMENTO E IA 
if df is not None and client:
    st.subheader("📊 Prévia dos Dados")
    st.dataframe(df.head(), use_container_width=True)

    if 'produto' in df.columns and 'valor' in df.columns:
        if st.button("🚀 Gerar Relatório com IA"):
            with st.spinner("A Luna está analisando os números..."):
                
                # A. Cálculos
                faturamento_total = df['valor'].sum()
                item_mais_vendido = df['produto'].mode()[0]
                ticket_medio = df['valor'].mean()

                # B. Gráfico Profissional
                fig, ax = plt.subplots(figsize=(10, 5))
                df.groupby('produto')['valor'].sum().sort_values().plot(kind='barh', color='#6a1b9a', ax=ax)
                plt.title("Faturamento por Categoria", fontsize=14)
                plt.xlabel("Valor Acumulado (R$)")
                plt.ylabel("Produto")
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                st.pyplot(fig)
                fig.savefig("temp_grafico.png")

                # C. Inteligência Artificial (Llama 3)
                prompt = f"""
                Você é um consultor de negócios sênior. Analise estes dados:
                - Faturamento Total: R$ {faturamento_total:.2f}
                - Produto de maior destaque: {item_mais_vendido}
                - Ticket Médio: R$ {ticket_medio:.2f}
                
                Crie um parágrafo de análise executiva e uma recomendação estratégica para o próximo mês.
                Seja direto e profissional.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                analise_ia = chat_completion.choices[0].message.content
                
                st.markdown("### 🤖 Insights da Luna AI")
                st.write(analise_ia)

                # D. Geração de PDF Seguro
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="RELATÓRIO DE PERFORMANCE - LUNA AI", ln=True, align='C')
                
                pdf.ln(10)
                pdf.image("temp_grafico.png", x=15, w=180)
                pdf.ln(10)

                pdf.set_font("Arial", size=12)
                # Garante que caracteres especiais não quebrem o PDF
                texto_limpo = analise_ia.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 8, txt=texto_limpo)

                pdf.output("Relatorio_Luna_AI.pdf")

                with open("Relatorio_Luna_AI.pdf", "rb") as f:
                    st.download_button(
                        label="📩 Baixar PDF Completo",
                        data=f,
                        file_name="Relatorio_Luna_AI.pdf",
                        mime="application/pdf"
                    )
    else:
        st.error("❌ Ops! A planilha precisa ter as colunas 'produto' e 'valor' (em minúsculo).")

st.divider()
st.caption("Luna AI Analytics | Versão 1.0 - Portfólio Andrea")