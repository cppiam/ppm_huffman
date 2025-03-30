class PPMModel:
    def __init__(self, alphabet, order):
        self.order = order
        self.contexts = {k: {} for k in range(1, order + 1)}  # {k: {contexto: {símbolo: contagem}}}
        self.k0_frequencies = {}  # {símbolo: contagem}
        self.alphabet = set(alphabet)
        self.seen_symbols = set()
        self.k0_unique_symbols = 0  # Conta símbolos únicos para k=0

    def update(self, symbol, history):
        # Atualiza k=-1
        if symbol not in self.seen_symbols:
            self.seen_symbols.add(symbol)
            self.k0_unique_symbols += 1  # Incrementa contador de símbolos únicos

        # Atualiza k=0
        if symbol not in self.k0_frequencies:
            self.k0_frequencies[symbol] = 0
        self.k0_frequencies[symbol] += 1

        # Atualiza k=1, k=2, ..., k=order
        for k in range(1, self.order + 1):
            if len(history) >= k:
                context = "".join(history[-k:])  # Contexto de tamanho k
                if context not in self.contexts[k]:
                    self.contexts[k][context] = {'symbols': set(), 'frequencies': {}}

                if symbol not in self.contexts[k][context]['symbols']:
                    self.contexts[k][context]['symbols'].add(symbol)

                if symbol not in self.contexts[k][context]['frequencies']:
                    self.contexts[k][context]['frequencies'][symbol] = 0
                self.contexts[k][context]['frequencies'][symbol] += 1

    def get_context_data(self, history):
        context_data = {}
        for k in range(self.order, 0, -1):
            if len(history) >= k:
                context = "".join(history[-k:])
                if context in self.contexts[k]:
                    context_data['context'] = context
                    context_data['symbols'] = self.contexts[k][context]['frequencies']
                    return context_data
        return None  # Retorna None se não encontrar contexto

    def print_tables(self, history):
        context_data = self.get_context_data(history)

        # Imprime tabelas k=order, k=order-1, ..., k=1
        for k in range(self.order, 0, -1):
            print(f"\n=== Contextos de Ordem {k} (k={k}) ===")
            print("Contexto   Simb.   Cont.   Prob.")
            for context in sorted(self.contexts[k].keys()):
                frequencies = self.contexts[k][context]['frequencies']
                unique_symbols = len(self.contexts[k][context]['symbols'])
                total = sum(frequencies.values())

                for symbol, count in sorted(frequencies.items()):
                    prob = count / (total + unique_symbols)
                    print(f"{context:<10} {symbol:<6} {count:<6} {prob:.4f}")
                print(f"{context:<10} esc    {unique_symbols:<6} {unique_symbols / (total + unique_symbols):.4f}")
                print("-" * 35)  # Linha de separação

        # Imprime tabela k=0
        print("\n=== Frequências de Ordem 0 (k=0) ===")
        print("Simb.   Cont.   Prob.")
        total = sum(self.k0_frequencies.values())
        if total + self.k0_unique_symbols > 0:
            for symbol, count in sorted(self.k0_frequencies.items()):
                prob = count / (total + self.k0_unique_symbols)
                print(f"{symbol:<6} {count:<6} {prob:.4f}")
            # Verifica se todos os símbolos foram vistos
            if len(self.seen_symbols) < len(self.alphabet):  # Apenas exibe 'esc' se nem todos os símbolos foram vistos
                print(f"esc    {self.k0_unique_symbols:<6} {self.k0_unique_symbols / (total + self.k0_unique_symbols):.4f}")
        else:
            print(f"esc    {self.k0_unique_symbols:<6} 0.0000")

        # Imprime tabela k=-1
        print("\n=== Símbolos Não Vistos (k=-1) ===")
        print("Simb.   Prob.")
        unseen = self.alphabet - self.seen_symbols
        if unseen:
            prob = 1.0 / len(unseen)
            for symbol in sorted(unseen):
                print(f"{symbol:<6} {prob:.4f}")
        else:
            print("(Todos os símbolos já foram vistos)")

        return context_data

def main():
    #alphabet = set('abcdefghijklmnopqrstuvwxyz ')
    alphabet = set('abcdr')
    text = input("Digite o texto: ")
    order = int(input("Digite a ordem do contexto (K): "))

    model = PPMModel(alphabet, order)

    print("Processando texto:", text)
    print("=" * 50)

    history = []
    for symbol in text:
        print(f"\nLendo: '{symbol}'")
        context_data = model.get_context_data(history)  # Obtém os dados do contexto antes de atualizar

        if context_data:
            print("\nDados do contexto de codificação:")
            print(f"Contexto: {context_data['context']}")
            print("Símbolos e contagens:", context_data['symbols'])

        model.update(symbol, history)  # Atualiza o modelo com o símbolo atual
        model.print_tables(history)  # Imprime as tabelas após a atualização
        history.append(symbol)

        input("\nPressione Enter para continuar...")
        import os
        os.system('cls')

if __name__ == "__main__":
    main()
