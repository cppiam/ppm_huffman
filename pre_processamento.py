import unicodedata
import re

def fix_double_encoding(text):
    try:
        return text.encode('latin1').decode('utf-8')
    except UnicodeError:
        return text

def remove_artifacts(text):
    # Removendo artefatos e convertendo tudo para minusculo
    
    # Primeiro tratar os travessões e outros símbolos especiais
    text = text.replace('â€”', ' ')  # Travessão -> espaço â€“
    text = text.replace('â€“', ' ')  # Travessão -> espaço
    text = text.replace('â€œ', ' ')  # Aspas esquerda -> espaço
    text = text.replace('â€', ' ')  # Aspas direita -> espaço
    text = text.replace('â€™', ' ')  # Apóstrofo -> espaço

    # Acentos agudos (á, é, í, ó, ú)
    text = text.replace('Ã', 'a')  # Á -> a
    text = text.replace('Ã¡', 'a')  # á -> a
    text = text.replace('Ã‰', 'e')  # É -> e
    text = text.replace('Ã©', 'e')  # é -> e
    text = text.replace('Ã', 'i')  # Í -> i
    text = text.replace('Ã­', 'i')  # í -> i
    text = text.replace('Ã“', 'o')  # Ó -> o
    text = text.replace('Ã³', 'o')  # ó -> o
    text = text.replace('Ãš', 'u')  # Ú -> u
    text = text.replace('Ãº', 'u')  # ú -> u

    # Acentos graves (à)
    text = text.replace('Ã€', 'a')  # À -> a
    text = text.replace('Ã ', 'a')  # à -> a
    text = text.replace('Ã¨', 'e')  # È -> e

    # Acentos circunflexos (â, ê, î, ô, û)
    text = text.replace('Ã‚', 'a')  # Â -> a
    text = text.replace('Ã¢', 'a')  # â -> a
    text = text.replace('Ãª', 'e')  # ê -> e
    text = text.replace('Ã®', 'i')  # î -> i
    text = text.replace('Ã´', 'o')  # ô -> o
    text = text.replace('Ã»', 'u')  # û -> u

    # Til (ã, õ)
    text = text.replace('Ãƒ', 'a')  # Ã -> a
    text = text.replace('Ã£', 'a')  # ã -> a
    text = text.replace('Ã±', 'n')  # ñ -> n
    text = text.replace('Ã•', 'o')  # Õ -> o
    text = text.replace('Ãµ', 'o')  # õ -> o
    
    # Cedilha (ç)
    text = text.replace('Ã‡', 'c')  # Ç -> c
    text = text.replace('Ã§', 'c')  # ç -> c

    # Trema (ü)
    text = text.replace('Ã¼', 'u')  # ü -> u
    text = text.replace("Âº", "") # nº

    # Remove todos os números substituindo por espaço
    text = re.sub(r'\d+', ' ', text)

    # Remove pontuação substituindo por espaço
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove espaços duplicados
    text = re.sub(r'\s+', ' ', text) 

    # Converte para minúsculas
    text = text.lower()

    # Remove espaços no início e fim
    text = text.strip()
    
    return text

def preprocess_text(input_file, output_file):
    """Main preprocessing function"""
    # Primeiro lemos como bytes para poder corrigir a dupla codificação
    with open(input_file, 'rb') as f:
        raw_text = f.read().decode('utf-8')
    
    # Corrigimos a dupla codificação
    text = fix_double_encoding(raw_text)
    
    # Aplicamos as outras transformações
    text = remove_artifacts(text)
    
    # Salvamos o texto processado
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == "__main__":
    input_file = "memorias.txt"
    output_file = "memorias_processed.txt"
    preprocess_text(input_file, output_file)
