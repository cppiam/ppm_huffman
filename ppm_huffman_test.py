import math
import struct
from huffman_simple import HuffmanSimple
from PPMSimples import PPMModel
from arquivo_utils import escrever_byte, escrever_bits_restantes

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
                    frequencies = self.ppm.contexts[k][context]['frequencies'].copy()
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
                    freq_for_huffman = {k: int(v) for k, v in frequencies.items()}  # Converte valores para inteiros
                    if unique_symbols > 0:
                        freq_for_huffman['esc'] = unique_symbols

                    # Verifica se todos os símbolos foram vistos
                    if len(frequencies) == len(self.ppm.alphabet):
                        freq_for_huffman.pop('esc', None)

                    self.huffman.build_tree(freq_for_huffman)

                    # Calcula a probabilidade do símbolo
                    if symbol in frequencies:
                        if codes:  # Se já tem códigos de escape acumulados
                            codes.append(self.huffman.codes[symbol])
                            return "".join(codes)
                        else:
                            return self.huffman.codes[symbol]
                    else:
                        codes.append(self.huffman.codes['esc'])

            # k = -1: equiprobabilidade para símbolos não vistos
            else:
                unseen = sorted(list(self.ppm.alphabet - self.ppm.seen_symbols))
                if unseen:
                    self.update_fixed_codes(unseen)
                    if len(unseen) == 1:
                        return "".join(codes) if codes else ""
                    if symbol in unseen:
                        
                        if codes:  # Se já tem códigos de escape
                            codes.append(self.fixed_codes[symbol])
                            return "".join(codes)
                        else:
                            return self.fixed_codes[symbol]

        return "".join(codes) if codes else None

def main():
    alphabet = set('abcdefghijklmnopqrstuvwxyz ')
    order = int(input("Digite a ordem do contexto (K): "))

    model = PPMHuffmanTest(alphabet, order)

    try:
        with open("memorias_processed.txt", "r") as arquivo:
            text = arquivo.read()
            print(f"Processando texto do arquivo 'memorias_processed.txt': '{text}'")
    except FileNotFoundError:
        print("Arquivo 'memorias_processed.txt' não encontrado.")
        return

    history = []
    bit_codificado = ""
    entropia = 0.0

    with open("arquivo_codificado.bin", "wb") as arquivo_codificado:
        # Codifica os símbolos
        for symbol in text:
            code = model.encode_symbol(symbol, history)
            if code:
                bit_codificado += code
                #print(f"Probabilidade do símbolo '{symbol}': {probabilidade}") # Imprime a probabilidade antes de somar
                #entropia += probabilidade * math.log2(1/probabilidade)

            model.ppm.update(symbol, history)
            history.append(symbol)

        # Calcula o número de símbolos
        num_simbolos = len(text)

        # Escreve o cabeçalho
        arquivo_codificado.write(struct.pack("<I", num_simbolos))  # '<I' indica inteiro little-endian de 4 bytes

        # Escreve os dados codificados
        while len(bit_codificado) >= 8:
            byte_para_escrever = bit_codificado[:8]
            escrever_byte(arquivo_codificado, byte_para_escrever)
            bit_codificado = bit_codificado[8:]
        escrever_bits_restantes(arquivo_codificado, bit_codificado)

    print("\nCodificação concluída. Dados escritos em 'arquivo_codificado.bin'.")
    print(f"Número de símbolos: {num_simbolos}") # Imprime o número de símbolos
    print(f"Número total de bits codificados: {len(bit_codificado)}") # Imprime o número total de bits codificados
    #print(f"Entropia: {entropia}")

if __name__ == "__main__":
    main()