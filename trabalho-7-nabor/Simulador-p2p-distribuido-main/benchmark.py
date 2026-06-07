import matplotlib.pyplot as plt
import statistics
from p2p_sim import P2PNetwork

# qts vezes repetir o random walk (aleatório) para tirar a média
REPETICOES_RW = 30


def medir(arquivo, start, recurso, ttl, algo, repeticoes=1):
    """Executa uma busca 'repeticoes' vezes recarregando a rede do zero a cada vez
    (cache limpo) e devolve a média de mensagens e a taxa de sucesso."""
    msgs = []
    sucessos = 0
    for _ in range(repeticoes):
        rede = P2PNetwork(arquivo)  # recarrega -> cache zerado, teste justo
        res = rede.search(start, recurso, ttl, algo)
        msgs.append(res["mensagens"])
        if res["sucesso"]:
            sucessos += 1
    media = statistics.mean(msgs) if msgs else 0
    taxa = (sucessos / repeticoes) * 100
    return media, taxa


def medir_cache_hit(arquivo, start, recurso, ttl, algo):
    """Roda a busca informada DUAS vezes na MESMA rede (sem recarregar):
    a 1ª preenche o cache (cache miss), a 2ª aproveita o cache (cache hit)."""
    rede = P2PNetwork(arquivo)
    r_miss = rede.search(start, recurso, ttl, algo)
    r_hit = rede.search(start, recurso, ttl, algo)
    return r_miss["mensagens"], r_hit["mensagens"]


def benchmark_rede(arquivo, start, recurso, ttl, titulo):
    """Roda todos os algoritmos para um cenário e devolve um dicionário de resultados."""
    print(f"\n=== {titulo} ===")
    print(f"Buscando '{recurso}' a partir de '{start}' (TTL={ttl})")
    print("-" * 50)

    resultados = {}

    # Flooding (determinístico, 1 execução basta)
    m, _ = medir(arquivo, start, recurso, ttl, "flooding")
    resultados["Flooding"] = m
    print(f"Flooding:                  {m:.1f} msgs")

    # Random Walk (aleatório -> média de várias rodadas)
    m, taxa = medir(arquivo, start, recurso, ttl, "random_walk", REPETICOES_RW)
    resultados["Random Walk"] = m
    print(f"Random Walk (média {REPETICOES_RW}x): {m:.1f} msgs | sucesso {taxa:.0f}%")

    # Informed Flooding: cache miss (1 busca) e cache hit (2 busca)
    miss, hit = medir_cache_hit(arquivo, start, recurso, ttl, "informed_flooding")
    resultados["Informed Flooding\n(1ª - miss)"] = miss
    resultados["Informed Flooding\n(2ª - cache)"] = hit
    print(f"Informed Flooding:         {miss} -> {hit} msgs (miss -> cache hit)")

    return resultados


def gerar_grafico(dados_por_rede):
    """Gera um gráfico com um subplot para cada cenário testado."""
    n = len(dados_por_rede)
    fig, axes = plt.subplots(1, n, figsize=(8 * n, 6))
    if n == 1:
        axes = [axes]

    cores = ['#3498db', '#e67e22', '#9b59b6', '#2ecc71']

    for ax, (titulo, resultados) in zip(axes, dados_por_rede.items()):
        nomes = list(resultados.keys())
        valores = list(resultados.values())
        barras = ax.bar(nomes, valores, color=cores[:len(nomes)])
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.set_ylabel("Número de Mensagens Trocadas")
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.tick_params(axis='x', labelsize=8)
        for barra in barras:
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width() / 2., altura,
                    f'{altura:.1f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig("resultado_benchmark.png", dpi=120, bbox_inches='tight')
    print("\n✅ Gráfico salvo como 'resultado_benchmark.png'")
    plt.show()


def run_benchmark():
    print("=== INICIANDO BENCHMARK AUTOMATIZADO ===")

    dados = {}
    # Rede pequena (6 nos)
    dados["Rede 6 nós — r6 distante (TTL 6)"] = benchmark_rede(
        "rede_teste.json", "n1", "r6", 6, "REDE PEQUENA (6 nós)")
    # Rede grande (12 nos)
    dados["Rede 12 nós — r17 distante (TTL 8)"] = benchmark_rede(
        "rede_teste2.json", "n1", "r17", 8, "REDE GRANDE (12 nós)")

    print("\nGerando gráfico comparativo...")
    gerar_grafico(dados)


if __name__ == "__main__":
    run_benchmark()