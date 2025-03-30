import math
import struct
from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel
from arquivo_utils import ler_byte

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
        for k in range(self.ppm.order, -1, -1):
            if k > 0:
                if len(history) < k:
                    continue
                context = "".join(history[-k:])
                if context not in self.ppm.contexts[k]:
                    continue
                
                frequencies = self.ppm.contexts[k][context]['frequencies'].copy()
                unique_symbols = len(self.ppm.contexts[k][context]['symbols'])

                # Exclusão: Remove símbolos vistos em contextos de ordem superior
                if k < self.ppm.order and len(history) >= k + 1:
                    higher_context = "".join(history[-(k + 1):])
                    if higher_context in self.ppm.contexts[k + 1]:
                        seen_higher = self.ppm.contexts[k + 1][higher_context]['symbols']
                        frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                        unique_symbols = len(set(frequencies.keys()))
            else:
                # k = 0
                frequencies = self.ppm.k0_frequencies.copy()
                unique_symbols = self.ppm.k0_unique_symbols

                # Exclusão: Remove símbolos vistos em contextos de ordem superior
                if self.ppm.order > 0 and len(history) >= 1:
                    higher_context = history[-1]
                    if higher_context in self.ppm.contexts[1]:
                        seen_higher = self.ppm.contexts[1][higher_context]['symbols']
                        frequencies = {s: f for s, f in frequencies.items() if s not in seen_higher}
                        unique_symbols = len(set(frequencies.keys()))

            if frequencies:
                freq_for_huffman = frequencies.copy()
                if unique_symbols > 0 and len(frequencies) < len(self.ppm.alphabet):
                    freq_for_huffman['esc'] = unique_symbols

                # Verifica se todos os símbolos foram vistos
                if len(frequencies) == len(self.ppm.alphabet):
                    freq_for_huffman.pop('esc', None)

                if not freq_for_huffman:
                    continue

                self.huffman.build_tree(freq_for_huffman)

                # Tenta decodificar com os códigos Huffman atuais
                current_code = ""
                remaining_bits = bitstream
                for bit in bitstream:
                    current_code += bit
                    remaining_bits = remaining_bits[1:]
                    if current_code in self.huffman.codes.values():
                        symbol = [s for s, c in self.huffman.codes.items() if c == current_code][0]
                        
                        if symbol == 'esc':
                            bitstream = remaining_bits
                            break
                        else:
                            return symbol, remaining_bits
        
        # k = -1: equiprobabilidade para símbolos não vistos (só se ainda houver símbolos não vistos)
        unseen = sorted(list(self.ppm.alphabet - self.ppm.seen_symbols))
        if unseen:
            # Caso especial: apenas um símbolo não visto
            if len(unseen) == 1:
                symbol = unseen[0]
                return symbol, bitstream
            
            bits_needed = math.ceil(math.log2(len(unseen)))
            
            if len(bitstream) >= bits_needed:
                fixed_code = bitstream[:bits_needed]
                
                self.update_fixed_codes(unseen)
                
                if fixed_code in self.reverse_fixed_codes:
                    symbol = self.reverse_fixed_codes[fixed_code]
                    return symbol, bitstream[bits_needed:]
        return None, bitstream

def main():
    alphabet = set('abcdr')
    order = int(input("Digite a ordem do contexto (K): "))

    decoder = PPMHuffmanDecoder(alphabet, order)
    
    history = []
    decoded_text = []
    bitstream = ""

    # Leitura do arquivo binário
    with open("arquivo_codificado.bin", "rb") as arquivo_codificado:
        # Lê o cabeçalho
        cabecalho = arquivo_codificado.read(4)
        if len(cabecalho) != 4:
            print("ERRO: Cabeçalho inválido.")
            return
        num_simbolos = struct.unpack("<I", cabecalho)[0]

        # Lê os dados codificados
        bitstream = ""
        while True:
            byte_lido = ler_byte(arquivo_codificado)
            if byte_lido is None:
                break
            bitstream += byte_lido

        # Decodifica os símbolos
        decoded_text = []
        history = []
        for _ in range(num_simbolos):
            symbol, bitstream = decoder.decode_symbol(bitstream, history)
            if symbol is None:
                print("ERRO: Decodificação interrompida.")
                break
            decoded_text.append(symbol)
            decoder.ppm.update(symbol, history)
            history.append(symbol)

    print("\nDecodificação concluída!")
    print(f"Texto original: {''.join(decoded_text)}")

if __name__ == "__main__":
    main()