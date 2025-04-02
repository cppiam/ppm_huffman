from heapq import heappush, heappop

class HuffmanNode:
    def __init__(self, symbol=None, frequency=0):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        # Compara pela frequência
        if self.frequency == other.frequency:
            # Desempata pela ordem alfabética dos símbolos, se ambos os nós forem folhas
            if self.symbol is not None and other.symbol is not None:
                return self.symbol < other.symbol
            # Se um dos nós for interno (symbol=None), não desempata por símbolo
            return self.symbol is not None  # Nós com símbolo vêm antes de nós internos
        return self.frequency < other.frequency

class HuffmanSimple:
    def __init__(self):
        self.codes = {}
        
    def build_tree(self, frequencies):
        # Cria fila de prioridade
        heap = []
        for symbol, freq in sorted(frequencies.items()):  # Ordena os símbolos para consistência
            node = HuffmanNode(symbol, freq)
            heappush(heap, node)

        # Constrói a árvore
        while len(heap) > 1:
            left = heappop(heap)
            right = heappop(heap)

            # Cria nó interno com frequência combinada
            parent = HuffmanNode(frequency=left.frequency + right.frequency)
            parent.left = left
            parent.right = right

            heappush(heap, parent)

        # Gera códigos
        self.codes = {}
        self._generate_codes(heap[0], "")
        
    def _generate_codes(self, node, code):
        if node is None:
            return
            
        if node.symbol is not None:
            self.codes[node.symbol] = code
            return
            
        self._generate_codes(node.left, code + "0")
        self._generate_codes(node.right, code + "1")
    
    def print_codes(self):
        print("\nCódigos Huffman:")
        print("-" * 20)
        for symbol, code in sorted(self.codes.items()):
            print(f"'{symbol}': {code}")
