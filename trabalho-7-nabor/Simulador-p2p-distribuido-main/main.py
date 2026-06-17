import os
from p2p_sim import P2PNetwork

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_dicas(rede):
    """Mostra o que existe na rede para ajudar o usuário."""
    if not rede: return
    
    print("\n--- DICAS (O que digitar?) ---")
    print(f"Nós disponíveis: {list(rede.nodes.keys())}")
    
    recursos = set()
    for node in rede.nodes.values():
        recursos.update(node.resources)
    print(f"Recursos na rede: {sorted(list(recursos))}")
    
    # Sugestão de TTL baseada no tamanho da rede
    ttl_sugerido = len(rede.nodes) // 2 + 2
    print(f"TTL Sugerido: {ttl_sugerido} (para rede de {len(rede.nodes)} nós)")
    print("------------------------------")

def main():
    rede = None
    arquivo_atual = "rede_teste.json" 

    while True:
        limpar_tela()
        print("=== SIMULADOR P2P - Trabalho 7 ===")
        print(f"Arquivo Atual: {arquivo_atual}")
        status = "Carregada ✅" if rede else "Não carregada ❌"
        print(f"Status da Rede: {status}")
        print("----------------------------------")
        print("1. Carregar/Validar Arquivo de Configuração")
        print("2. Realizar Busca (Flooding)")
        print("3. Realizar Busca (Random Walk)")
        print("4. Realizar Busca Informada (Informed Flooding)")
        print("5. Realizar Busca Informada (Informed Random Walk)")
        print("6. Visualizar Rede (Gráfico)")
        print("7. Animar Busca (Bônus)")
        print("0. Sair")
        print("----------------------------------")
        
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                path = input(f"Digite o nome do arquivo [Enter para '{arquivo_atual}']: ")
                if path: arquivo_atual = path
                try:
                    rede = P2PNetwork(arquivo_atual)
                    input("\n✅ Rede carregada com sucesso! Pressione Enter...")
                except Exception as e:
                    print(f"\n❌ Erro ao carregar arquivo: {e}")
                    input("Pressione Enter...")

            elif opcao == '0':
                print("Saindo...")
                break

            elif not rede:
                input("\n⚠️ ERRO: Você precisa carregar a rede primeiro (Opção 1)! Enter para voltar...")
                continue

            elif opcao in ['2', '3', '4', '5', '7']:
                mostrar_dicas(rede)

                node_id = input("ID do nó inicial (ex: n1): ")
                resource = input("Nome do recurso (ex: r6): ")
                
                print("\n[Dica: TTL é o 'tempo de vida'. Define quantos saltos a mensagem pode dar.]")
                print("[Se for muito baixo (ex: 1), a busca morre cedo. Se for alto, vai longe.]")
                ttl_str = input("Digite o TTL (Enter para usar 5): ")
                ttl = int(ttl_str) if ttl_str else 5
                
                algo_map = {
                    '2': 'flooding',
                    '3': 'random_walk',
                    '4': 'informed_flooding',
                    '5': 'informed_random_walk'
                }

                if opcao == '7':
                    print("\nEscolha o algoritmo para animar:")
                    print("1. Flooding (Explora tudo ao redor)")
                    print("2. Random Walk (Vai de um em um)")
                    escolha_anim = input("Opção [1]: ")
                    algo_anim = 'flooding' if escolha_anim != '2' else 'random_walk'
                    
                    print("\n🎥 A janela da animação será aberta. Feche-a para voltar ao menu.")
                    rede.animate_search(node_id, resource, ttl, algo_anim)
                else:
                    algo = algo_map[opcao]
                    resultado = rede.search(node_id, resource, ttl, algo)
                    
                    print("\n--- RESULTADO DA BUSCA ---")
                    if resultado:
                        print(f"Algoritmo: {algo}")
                        print(f"Sucesso: {'✅ Sim' if resultado['sucesso'] else '❌ Não'}")
                        print(f"Nó Destino: {resultado['nó_destino']}")
                        print(f"Mensagens Trocadas: {resultado['mensagens']}")
                        print(f"Nós Envolvidos: {resultado['nós_envolvidos']}")
                    input("\nPressione Enter para voltar...")

            elif opcao == '6':
                print("\n🖼️ A janela do gráfico será aberta. Feche-a para voltar ao menu.")
                rede.draw_network()

        except Exception as e:
            input(f"\n❌ Ocorreu um erro: {e}. Pressione Enter...")

if __name__ == "__main__":
    main()