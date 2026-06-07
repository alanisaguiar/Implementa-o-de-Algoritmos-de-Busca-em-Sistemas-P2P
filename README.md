# Simulador de Redes P2P — Algoritmos de Busca

## Equipe C:

- Alanis Aguiar Bitencourt - 2315059
- Gabriel Costa Castro - 2314515
- Lívia Catarina Macedo - 2315085

## Funcionalidades

1. **Carregamento de Topologia:** leitura de arquivos JSON que definem o número de
   nós, os limites de vizinhos, os recursos de cada nó e as arestas da rede.
2. **Validação da rede:** após a leitura, o programa verifica que:
   - a rede não está particionada (existe caminho entre quaisquer dois nós);
   - cada nó respeita os limites `min_neighbors` e `max_neighbors`;
   - nenhum nó está sem recursos;
   - não há arestas de um nó para ele mesmo (self-loops).
3. **Algoritmos de busca implementados:**
   - **Flooding (Inundação):** propaga a requisição para todos os vizinhos.
     Sempre encontra o recurso dentro do alcance do TTL, mas gera muito tráfego.
   - **Random Walk (Passeio Aleatório):** encaminha a requisição a um vizinho
     escolhido aleatoriamente. Gera menos tráfego, mas não garante sucesso.
   - **Informed Flooding (Inundação Informada):** usa um cache local em cada nó
     para acelerar buscas por recursos cuja localização já é conhecida.
   - **Informed Random Walk (Passeio Aleatório Informado):** durante o passeio,
     cada nó visitado consulta seu cache; se já souber onde está o recurso, segue
     direto até ele em vez de continuar sorteando.
4. **Controle por TTL:** todas as buscas aceitam um parâmetro Time to Live que
   limita o número de saltos da requisição na rede.
5. **Relatório de cada busca:** ao final, o programa informa se o recurso foi
   encontrado, o número total de mensagens trocadas e o número total de nós
   envolvidos.
6. **Visualização (opcional):**
   - desenho estático da topologia da rede (NetworkX + Matplotlib);
   - animação em tempo real da propagação das mensagens durante a busca;
   - benchmark automatizado que compara os algoritmos e gera gráficos.

## Topologias de Teste

O simulador foi testado em duas topologias de tamanhos diferentes, ambas válidas
(conexas, com 2 a 4 vizinhos por nó e todos os nós com recursos):

**Rede pequena (6 nós) — `rede_teste.json`:**

![Topologia 6 nós](imgs/topologia_6nos.png)

**Rede grande (12 nós) — `rede_teste2.json`:**

![Topologia 12 nós](imgs/topologia_12nos.png)

## Como Rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o menu interativo
Para carregar a rede, validar, fazer buscas e ver as visualizações:
```bash
python main.py
```

No menu é possível escolher o nó inicial, o recurso buscado, o TTL e o algoritmo
de busca, além de visualizar a rede e animar uma busca.

### 3. Gerar os gráficos de comparação
```bash
python benchmark.py
```

## Resultados Obtidos

Os testes mediram o número de mensagens trocadas por cada algoritmo, em ambas as
redes, buscando recursos próximos e distantes do nó inicial.

| Algoritmo | 6 nós (r3 próximo) | 6 nós (r6 distante) | 12 nós (r3 próximo) | 12 nós (r17 distante) |
|---|---|---|---|---|
| Flooding | 2 | 5 | 2 | 11 |
| Random Walk (média) | 4.0 | 4.0 | 3.3 | 8.0 |
| Informed Flooding (1ª busca) | 2 | 5 | 2 | 11 |
| Informed Flooding (2ª busca, cache) | 1 | 2 | 1 | 6 |

Principais observações:

- **Flooding:** sempre encontra o recurso dentro do TTL, mas o custo cresce com o
  tamanho da rede e a distância do recurso, chegando a envolver todos os nós.
- **Random Walk:** gera menos tráfego em alguns casos, porém é instável — sua taxa
  de sucesso cai bastante quando o recurso está distante (na rede de 12 nós, quase
  sempre falha em encontrar o recurso dentro do TTL).
- **Busca Informada:** o cache reduz o custo das buscas repetidas. Na segunda busca
  por um mesmo recurso, o número de mensagens cai para o tamanho do caminho mais
  curto até o recurso (por exemplo, de 11 para 6 mensagens na rede grande).

![Benchmark comparativo](imgs/resultado_benchmark.png)
