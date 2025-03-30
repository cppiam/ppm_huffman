import math
from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel

class PPMHuffmanTest:
    def __init__(self, alphabet, order):
        self.ppm = PPMModel(alphabet, order)
        self.huffman = HuffmanSimple()
        self.encoded_bits = []
        self.fixed_codes = {}

    def update_fixed_codes(self, unseen):
        bits_per_symbol = math.ceil(math.log2(len(unseen)))
        for i, symbol in enumerate(sorted(unseen)):
            self.fixed_codes[symbol] = bin(i)[2:].zfill(bits_per_symbol)

    def encode_symbol(self, symbol, history):
        print(f"\nBuscando codificação para símbolo: '{symbol}'")
        codes = []  # Lista para armazenar os códigos gerados

        # Verifica contextos de k=order até k=-1
        for k in range(self.ppm.order, -2, -1):
            if k >= 0:
                # Para k > 0, verifica contexto específico
                if k > 0:
                    if len(history) < k:
                        continue
                    context = "".join(history[-k:])
                    if context not in self.ppm.contexts[k]:
                        continue
                    frequencies = self.ppm.contexts[k][context]['frequencies'].copy()  # Cria uma cópia para não alterar o original
                    unique_symbols = len(self.ppm.contexts[k][context]['symbols'])

                    # Exclusão: Remove símbolos vistos em contextos de ordem superior
                    if k < self.ppm.order and len(history) >= k + 1:
                        higher_context = "".join(history[-(k + 1):])
                        if higher_context in self.ppm.contexts[k + 1]:
                            seen_higher = self.ppm.contexts[k + 1][higher_context]['symbols']
                            frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                            unique_symbols = len(set(frequencies.keys()))

                # Para k = 0
                else:
                    frequencies = self.ppm.k0_frequencies.copy()  # Cria uma cópia para não alterar o original
                    unique_symbols = self.ppm.k0_unique_symbols

                    # Exclusão: Remove símbolos vistos em contextos de ordem superior
                    if self.ppm.order > 0 and len(history) >= 1:
                        higher_context = history[-1]
                        if higher_context in self.ppm.contexts[1]:
                            seen_higher = self.ppm.contexts[1][higher_context]['symbols']
                            frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                            unique_symbols = len(set(frequencies.keys()))

                if frequencies:
                    print(f"\nTestando ordem {k}")
                    freq_for_huffman = frequencies.copy()
                    if unique_symbols > 0:
                        freq_for_huffman['esc'] = unique_symbols

                    print("Frequências para codificação:")
                    for sym, freq in sorted(freq_for_huffman.items()):
                        print(f"'{sym}': {freq}")

                    # Verifica se todos os símbolos foram vistos
                    if len(frequencies) == len(self.ppm.alphabet):
                        print("Todos os símbolos vistos, removendo 'esc' da codificação.")
                        freq_for_huffman.pop('esc', None)

                    self.huffman.build_tree(freq_for_huffman)
                    self.huffman.print_codes()

                    # Verifica se o símbolo está presente nas frequências *após* a exclusão
                    if symbol in frequencies:
                        print(f"Símbolo encontrado! Codificando '{symbol}'")
                        return self.huffman.codes[symbol]
                    else:
                        print("Símbolo não encontrado. Codificando escape.")
                        codes.append(self.huffman.codes['esc'])
                        # Não retorna aqui, continua para codificar o símbolo no k=-1

            # k = -1: equiprobabilidade para símbolos não vistos
            else:
                unseen = sorted(list(self.ppm.alphabet - self.ppm.seen_symbols))
                if unseen:
                    print("\nUsando ordem -1 (equiprobabilidade)")
                    self.update_fixed_codes(unseen)
                    if len(unseen) == 1:  # Verifica se há apenas um símbolo restante
                        print(f"Apenas um símbolo restante em k=-1: '{unseen[0]}'. Omitindo codificação.")
                        return "".join(codes)  # Retorna apenas os códigos de escape
                    if symbol in unseen:
                        print(f"Codificando símbolo não visto '{symbol}': {self.fixed_codes[symbol]}")
                        codes.append(self.fixed_codes[symbol])
                        return "".join(codes)  # Retorna escape + código do símbolo
                else:
                    print("(Todos os símbolos já foram vistos)")

        return "".join(codes) if codes else None

    def print_ppm_tables(self, history):
        # Imprime tabelas k=order, k=order-1, ..., k=1
        for k in range(self.ppm.order, 0, -1):
            print(f"\n=== Contextos de Ordem {k} (k={k}) ===")
            print("Contexto   Simb.   Cont.   Prob.")
            for context in sorted(self.ppm.contexts[k].keys()):
                frequencies = self.ppm.contexts[k][context]['frequencies']
                unique_symbols = len(self.ppm.contexts[k][context]['symbols'])
                total = sum(frequencies.values())

                for symbol, count in sorted(frequencies.items()):
                    prob = count / (total + unique_symbols)
                    print(f"{context:<10} {symbol:<6} {count:<6} {prob:.4f}")
                print(f"{context:<10} esc    {unique_symbols:<6} {unique_symbols / (total + unique_symbols):.4f}")
                print("-" * 35)  # Linha de separação

        # Imprime tabela k=0
        print("\n=== Frequências de Ordem 0 (k=0) ===")
        print("Simb.   Cont.   Prob.")
        total = sum(self.ppm.k0_frequencies.values())
        if total + self.ppm.k0_unique_symbols > 0:
            for symbol, count in sorted(self.ppm.k0_frequencies.items()):
                prob = count / (total + self.ppm.k0_unique_symbols)
                print(f"{symbol:<6} {count:<6} {prob:.4f}")
            # Verifica se todos os símbolos foram vistos
            if len(self.ppm.seen_symbols) == len(self.ppm.alphabet):
                print("-" * 35)  # Linha de separação
            else:
                print(f"esc    {self.ppm.k0_unique_symbols:<6} {self.ppm.k0_unique_symbols / (total + self.ppm.k0_unique_symbols):.4f}")

        # Imprime tabela k=-1
        print("\n=== Símbolos Não Vistos (k=-1) ===")
        print("Simb.   Prob.")
        unseen = self.ppm.alphabet - self.ppm.seen_symbols
        if unseen:
            prob = 1.0 / len(unseen)
            for symbol in sorted(unseen):
                print(f"{symbol:<6} {prob:.4f}")
        else:
            print("(Todos os símbolos já foram vistos)")

def main():
    alphabet = set('abcdr')
    text = input("Digite o texto: ")
    order = int(input("Digite a ordem do contexto (K): "))

    model = PPMHuffmanTest(alphabet, order)

    print(f"Processando texto: '{text}'")
    print("=" * 50)

    history = []
    encoded_bits = []

    for symbol in text:
        print(f"\nProcessando símbolo: '{symbol}'")
        print(f"Histórico atual: {history}")

        # Codifica
        code = model.encode_symbol(symbol, history)
        if code:
            print(f"Código gerado: {code}")
            encoded_bits.append(code)

        # Atualiza modelo PPM
        model.ppm.update(symbol, history)
        # Mostra tabelas atualizadas
        model.print_ppm_tables(history)

        history.append(symbol)

        print("\nMensagem codificada até agora:", "".join(encoded_bits))
        input("\nPressione Enter para continuar...")
        import os
        os.system('cls')

if __name__ == "__main__":
    main()
