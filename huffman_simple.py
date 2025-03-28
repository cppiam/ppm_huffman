from heapq import heappush, heappop

class HuffmanNode:
    def __init__(self, symbol=None, frequency=0):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.frequency < other.frequency

class HuffmanSimple:
    def __init__(self):
        self.codes = {}
        
    def build_tree(self, frequencies):
        """
        Constrói árvore Huffman a partir de um dicionário de frequências
        frequencies = {'a': 5, 'b': 2, ...}
        """
        # Cria fila de prioridade
        heap = []
        for symbol, freq in frequencies.items():
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

def main():
    # Exemplo simples
    frequencies = {
        'a': 5,
        'b': 2,
        'r': 3,
        'c': 1,
        'd': 1
    }
    
    print("Frequências:")
    for symbol, freq in sorted(frequencies.items()):
        print(f"'{symbol}': {freq}")
    
    huffman = HuffmanSimple()
    huffman.build_tree(frequencies)
    huffman.print_codes()

if __name__ == "__main__":
    main()