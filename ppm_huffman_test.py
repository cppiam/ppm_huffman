from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel

class PPMHuffmanTest:
    def __init__(self, alphabet, order):
        self.ppm = PPMModel(alphabet, order)
        self.huffman = HuffmanSimple()
        self.encoded_bits = []

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
                    frequencies = self.ppm.contexts[k][context]['frequencies']
                    unique_symbols = len(self.ppm.contexts[k][context]['symbols'])

                # Para k = 0
                else:
                    frequencies = self.ppm.k0_frequencies
                    unique_symbols = self.ppm.k0_unique_symbols

                if frequencies:
                    print(f"\nTestando ordem {k}")
                    freq_for_huffman = frequencies.copy()
                    if unique_symbols > 0:
                        freq_for_huffman['esc'] = unique_symbols

                    print("Frequências para codificação:")
                    for sym, freq in sorted(freq_for_huffman.items()):
                        print(f"'{sym}': {freq}")

                    self.huffman.build_tree(freq_for_huffman)
                    self.huffman.print_codes()

                    if symbol in frequencies:
                        print(f"Símbolo encontrado! Codificando '{symbol}'")
                        return self.huffman.codes[symbol]
                    else:
                        print("Símbolo não encontrado. Codificando escape.")
                        codes.append(self.huffman.codes['esc'])
                        # Não retorna aqui, continua para codificar o símbolo no k=-1

            # k = -1: equiprobabilidade para símbolos não vistos
            else:
                unseen = self.ppm.alphabet - self.ppm.seen_symbols
                if unseen:
                    freq_for_huffman = {sym: 1 for sym in unseen}
                    print("\nUsando ordem -1 (equiprobabilidade)")
                    print("Frequências:")
                    for sym, freq in sorted(freq_for_huffman.items()):
                        print(f"'{sym}': {freq}")

                    self.huffman.build_tree(freq_for_huffman)
                    self.huffman.print_codes()

                    if symbol in unseen:
                        print(f"Codificando símbolo não visto '{symbol}'")
                        codes.append(self.huffman.codes[symbol])
                        return "".join(codes)  # Retorna escape + código do símbolo

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
    alphabet = set('abcdr')  # Alfabeto reduzido para teste
    text = "abracadabra"
    order = 2

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