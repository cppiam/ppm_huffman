from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel

class PPMHuffmanTest:
    def __init__(self, alphabet, order):
        self.ppm = PPMModel(alphabet, order)
        self.huffman = HuffmanSimple()
        self.encoded_bits = []

    def encode_symbol(self, symbol, history):
        print(f"\nBuscando codificação para símbolo: '{symbol}'")
        
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
                    # Prepara frequências para Huffman
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
                        return self.huffman.codes['esc']
            
            # k = -1: equiprobabilidade para símbolos não vistos
            else:
                unseen = self.ppm.alphabet - self.ppm.seen_symbols
                if unseen:
                    # Cria frequências uniformes
                    freq_for_huffman = {sym: 1 for sym in unseen}
                    print("\nUsando ordem -1 (equiprobabilidade)")
                    print("Frequências:")
                    for sym, freq in sorted(freq_for_huffman.items()):
                        print(f"'{sym}': {freq}")
                    
                    self.huffman.build_tree(freq_for_huffman)
                    self.huffman.print_codes()
                    
                    if symbol in unseen:
                        print(f"Codificando símbolo não visto '{symbol}'")
                        return self.huffman.codes[symbol]
        
        return None

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
        model.ppm.print_tables(history)
        
        history.append(symbol)
        
        print("\nMensagem codificada até agora:", "".join(encoded_bits))
        input("\nPressione Enter para continuar...")
        import os
        os.system('cls')

if __name__ == "__main__":
    main()