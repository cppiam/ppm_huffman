import math
from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel

class PPMHuffmanDecoder:
    def __init__(self, alphabet, order):
        self.ppm = PPMModel(alphabet, order)
        self.huffman = HuffmanSimple()
        self.fixed_codes = {}
        self.reverse_fixed_codes = {}
        
    def update_fixed_codes(self, unseen):
        bits_per_symbol = math.ceil(math.log2(len(unseen)))
        self.fixed_codes = {}
        self.reverse_fixed_codes = {}
        for i, symbol in enumerate(sorted(unseen)):
            code = bin(i)[2:].zfill(bits_per_symbol)
            self.fixed_codes[symbol] = code
            self.reverse_fixed_codes[code] = symbol
    
    def decode_symbol(self, bitstream, history):
        print(f"\n[DEBUG] Decodificando símbolo do bitstream: {bitstream}")
        print(f"[DEBUG] Histórico atual: {history}")
        
        # Mostra informações detalhadas sobre os símbolos não vistos
        unseen = sorted(list(self.ppm.alphabet - self.ppm.seen_symbols))
        print("\n[DEBUG] Símbolos não vistos (k=-1):")
        
        # Verificação inicial de símbolos não vistos (apenas para debug)
        if unseen:
            if len(unseen) == 1:
                print(f"[DEBUG] Único símbolo não visto: '{unseen[0]}'")
            else:
                bits_needed = math.ceil(math.log2(len(unseen)))
                print(f"Bits necessários por símbolo: {bits_needed}")
                print("Tabela de códigos fixos:")
                self.update_fixed_codes(unseen)
                for symbol, code in sorted(self.fixed_codes.items()):
                    print(f"'{symbol}': {code}")
        else:
            print("(Todos os símbolos já foram vistos)")
        
        # Verifica contextos de k=order até k=0
        for k in range(self.ppm.order, -1, -1):
            print(f"\n[DEBUG] Testando ordem {k}")
            
            if k > 0:
                if len(history) < k:
                    print(f"[DEBUG] Histórico muito curto para ordem {k}")
                    continue
                context = "".join(history[-k:])
                print(f"[DEBUG] Contexto para ordem {k}: '{context}'")
                if context not in self.ppm.contexts[k]:
                    print(f"[DEBUG] Contexto '{context}' não encontrado na ordem {k}")
                    continue
                
                frequencies = self.ppm.contexts[k][context]['frequencies'].copy()
                unique_symbols = len(self.ppm.contexts[k][context]['symbols'])
                print(f"[DEBUG] Frequências no contexto '{context}': {frequencies}")
                print(f"[DEBUG] Símbolos únicos: {unique_symbols}")

                # Exclusão: Remove símbolos vistos em contextos de ordem superior
                if k < self.ppm.order and len(history) >= k + 1:
                    higher_context = "".join(history[-(k + 1):])
                    if higher_context in self.ppm.contexts[k + 1]:
                        seen_higher = self.ppm.contexts[k + 1][higher_context]['symbols']
                        print(f"[DEBUG] Símbolos vistos em ordem superior ({k+1}): {seen_higher}")
                        frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                        unique_symbols = len(set(frequencies.keys()))
                        print(f"[DEBUG] Frequências após exclusão: {frequencies}")
                        print(f"[DEBUG] Símbolos únicos após exclusão: {unique_symbols}")
            else:
                # k = 0
                frequencies = self.ppm.k0_frequencies.copy()
                unique_symbols = self.ppm.k0_unique_symbols
                print(f"[DEBUG] Frequências de ordem 0: {frequencies}")
                print(f"[DEBUG] Símbolos únicos em ordem 0: {unique_symbols}")

                # Exclusão: Remove símbolos vistos em contextos de ordem superior
                if self.ppm.order > 0 and len(history) >= 1:
                    higher_context = history[-1]
                    if higher_context in self.ppm.contexts[1]:
                        seen_higher = self.ppm.contexts[1][higher_context]['symbols']
                        print(f"[DEBUG] Símbolos vistos em ordem 1: {seen_higher}")
                        frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                        unique_symbols = len(set(frequencies.keys()))
                        print(f"[DEBUG] Frequências após exclusão: {frequencies}")
                        print(f"[DEBUG] Símbolos únicos após exclusão: {unique_symbols}")

            if frequencies:
                print(f"\n[DEBUG] Construindo árvore Huffman para ordem {k}")
                freq_for_huffman = frequencies.copy()
                if unique_symbols > 0 and len(frequencies) < len(self.ppm.alphabet):
                    freq_for_huffman['esc'] = unique_symbols
                    print("[DEBUG] Adicionando símbolo 'esc' com frequência:", unique_symbols)

                # Verifica se todos os símbolos foram vistos
                if len(frequencies) == len(self.ppm.alphabet):
                    print("[DEBUG] Todos os símbolos foram vistos, removendo 'esc'")
                    freq_for_huffman.pop('esc', None)

                if not freq_for_huffman:
                    print("[DEBUG] Nenhuma frequência disponível para construir árvore")
                    continue

                self.huffman.build_tree(freq_for_huffman)
                print("[DEBUG] Códigos Huffman gerados:")
                for symbol, code in sorted(self.huffman.codes.items()):
                    print(f"  '{symbol}': {code}")

                # Tenta decodificar com os códigos Huffman atuais
                current_code = ""
                remaining_bits = bitstream
                for bit in bitstream:
                    current_code += bit
                    remaining_bits = remaining_bits[1:]
                    if current_code in self.huffman.codes.values():
                        symbol = [s for s, c in self.huffman.codes.items() if c == current_code][0]
                        print(f"[DEBUG] Código encontrado: '{symbol}' ({current_code})")
                        
                        if symbol == 'esc':
                            print("[DEBUG] Símbolo escape encontrado. Indo para ordem inferior.")
                            bitstream = remaining_bits
                            break
                        else:
                            return symbol, remaining_bits
                    else:
                        print(f"[DEBUG] Código parcial '{current_code}' não corresponde a nenhum símbolo")
        
        # k = -1: equiprobabilidade para símbolos não vistos (só se ainda houver símbolos não vistos)
        print("\n[DEBUG] Usando ordem -1 (equiprobabilidade)")
        unseen = sorted(list(self.ppm.alphabet - self.ppm.seen_symbols))
        if unseen:
            # Caso especial: apenas um símbolo não visto
            if len(unseen) == 1:
                symbol = unseen[0]
                print(f"[DEBUG] Único símbolo não visto: '{symbol}' - decodificação determinística")
                # Verifica se há bits de escape pendentes (só aplica se veio de um contexto superior)
                if len(history) > 0:
                    print("[DEBUG] Há histórico - verificando necessidade de escape")
                    # Precisamos verificar se o escape foi codificado
                    # Como não temos essa informação, assumimos que foi
                    # Então precisaríamos consumir o código do escape primeiro
                    # Isso é complexo e pode exigir mudanças no codificador
                    # Solução simplificada: apenas retornar o símbolo
                return symbol, bitstream
                
            bits_needed = math.ceil(math.log2(len(unseen)))
            print(f"[DEBUG] Bits necessários: {bits_needed}")
            print(f"[DEBUG] Bitstream disponível: {bitstream}")
            
            if len(bitstream) >= bits_needed:
                fixed_code = bitstream[:bits_needed]
                print(f"[DEBUG] Tentando decodificar código fixo: {fixed_code}")
                
                self.update_fixed_codes(unseen)
                print("[DEBUG] Tabela de códigos fixos:")
                for sym, code in sorted(self.fixed_codes.items()):
                    print(f"  '{sym}': {code}")
                
                if fixed_code in self.reverse_fixed_codes:
                    symbol = self.reverse_fixed_codes[fixed_code]
                    print(f"[DEBUG] Símbolo decodificado: '{symbol}'")
                    return symbol, bitstream[bits_needed:]
                else:
                    print("[DEBUG] Código fixo não encontrado na tabela")
            else:
                print("[DEBUG] Bitstream insuficiente para decodificar símbolo não visto")
        else:
            print("[DEBUG] Todos os símbolos já foram vistos")

        print("[DEBUG] Nenhum símbolo pôde ser decodificado")
        return None, bitstream

def main():
    alphabet = set('abcdr')
    encoded_bits = input("Digite os bits codificados: ")
    order = int(input("Digite a ordem do contexto (K): "))

    decoder = PPMHuffmanDecoder(alphabet, order)
    
    history = []
    decoded_text = []
    bitstream = encoded_bits
    
    while bitstream:
        print("\n" + "=" * 50)
        print(f"Bitstream restante: {bitstream}")
        print(f"Histórico: {history}")
        print(f"Texto decodificado até agora: {''.join(decoded_text)}")
        
        # Mostra tabelas PPM atuais
        print("\nTabelas PPM atuais:")
        decoder.ppm.print_tables(history)
        
        symbol, bitstream = decoder.decode_symbol(bitstream, history)
        if symbol is None:
            print("Não foi possível decodificar mais símbolos.")
            break
            
        decoded_text.append(symbol)
        decoder.ppm.update(symbol, history)
        history.append(symbol)
        
        input("\nPressione Enter para continuar...")
        import os
        os.system('cls')
    
    print("\nDecodificação concluída!")
    print(f"Texto original: {''.join(decoded_text)}")

if __name__ == "__main__":
    main()