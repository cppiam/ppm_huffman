def escrever_byte(arquivo, bits):
    """
    Escreve um byte (8 bits) no arquivo.

    Args:
        arquivo (file): Objeto de arquivo aberto para escrita binária.
        bits (str): String contendo 8 bits.
    """
    if len(bits) != 8:
        raise ValueError("Um byte deve conter exatamente 8 bits.")

    byte = int(bits, 2).to_bytes(1, byteorder='big')
    arquivo.write(byte)

def escrever_bits_restantes(arquivo, bits):
    """
    Escreve os bits restantes (menos de 8) no arquivo, completando com zeros.

    Args:
        arquivo (file): Objeto de arquivo aberto para escrita binária.
        bits (str): String contendo os bits restantes.
    """
    if bits:
        bits = bits.ljust(8, '0')  # Completa com zeros à direita
        escrever_byte(arquivo, bits)

def ler_byte(arquivo):
    """
    Lê um byte do arquivo e retorna como uma string de 8 bits.

    Args:
        arquivo (file): Objeto de arquivo aberto para leitura binária.

    Returns:
        str: String contendo 8 bits lidos do arquivo, ou None se EOF.
    """
    byte = arquivo.read(1)
    if not byte:
        return None  # Fim do arquivo

    return bin(byte[0])[2:].zfill(8)