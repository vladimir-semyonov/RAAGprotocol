import uuid

# Определяем класс RAAG для представления группы Артина с правыми углами
class RAAG:
    def __init__(self, generators, commuting_pairs):
        # Множество образующих группы
        self.generators = set(generators)
        # Множество коммутативных пар, приведенных к сортированному виду
        self.commuting_pairs = set(tuple(sorted(pair)) for pair in commuting_pairs)
        # Расширенное множество образующих, включающее инверсии
        self.extended_generators = self.generators.union({g + "^-1" for g in self.generators})

    # Проверяет, коммутируют ли два элемента (учитывая инверсии)
    def are_commuting(self, a, b):
        a_base = a.replace("^-1", "")
        b_base = b.replace("^-1", "")
        return tuple(sorted((a_base, b_base))) in self.commuting_pairs or a_base == b_base

    # Возвращает инверсию элемента (g -> g^-1, g^-1 -> g)
    def inverse(self, g):
        return g[:-3] if g.endswith("^-1") else g + "^-1"

# Класс для представления элементов RAAG
class RAAGElement:
    def __init__(self, raag, word):
        # Проверяем допустимость слова
        if not all(g in raag.extended_generators for g in word):
            raise ValueError("Слово содержит недопустимые образующие или инверсии.")
        self.raag = raag
        self.word = list(word)
        # Приводим слово к нормальной форме
        self.reduce()

    # Приводит слово к нормальной форме: удаляет g g^-1, переставляет коммутирующие элементы
    def reduce(self):
        changed = True
        while changed:
            changed = False
            i = 0
            new_word = []
            while i < len(self.word):
                if i + 1 < len(self.word):
                    a, b = self.word[i], self.word[i + 1]
                    # Удаляем пары g g^-1 или g^-1 g
                    if self.raag.inverse(a) == b:
                        i += 2
                        changed = True
                        continue
                    # Переставляем коммутирующие элементы для нормальной формы
                    if self.raag.are_commuting(a, b):
                        a_base = a.replace("^-1", "")
                        b_base = b.replace("^-1", "")
                        if a_base > b_base:
                            new_word.append(b)
                            new_word.append(a)
                            i += 2
                            changed = True
                            continue
                new_word.append(self.word[i])
                i += 1
            if new_word != self.word:
                changed = True
            self.word = new_word

    # Строковое представление элемента (пустое слово отображается как "e")
    def __str__(self):
        return " ".join(self.word) if self.word else "e"

    # Возвращает инверсию элемента (меняет порядок и инвертирует каждый символ)
    def inverse(self):
        inv_word = [self.raag.inverse(g) for g in reversed(self.word)]
        return RAAGElement(self.raag, inv_word)

# Класс для представления гомоморфизма между RAAG
class RAAGHomomorphism:
    def __init__(self, domain_raag, codomain_raag, mapping):
        self.domain_raag = domain_raag
        self.codomain_raag = codomain_raag
        self.mapping = mapping
        # Проверяем корректность отображения
        self._verify_mapping()
        # Проверяем сохранение коммутативности
        self._verify_homomorphism()

    # Проверяет, что все образующие имеют образы, и они допустимы
    def _verify_mapping(self):
        for g in self.domain_raag.generators:
            if g not in self.mapping:
                raise ValueError(f"Генератор {g} не имеет образа в отображении.")
            for w in self.mapping[g]:
                if w not in self.codomain_raag.extended_generators:
                    raise ValueError(f"Образ {w} для {g} не является допустимым генератором.")

    # Проверяет, что гомоморфизм сохраняет коммутативность
    def _verify_homomorphism(self):
        for g1 in self.domain_raag.generators:
            for g2 in self.domain_raag.generators:
                # Пропускаем проверку для одинаковых образующих
                if g1 == g2:
                    continue
                if self.domain_raag.are_commuting(g1, g2):
                    image_g1 = RAAGElement(self.codomain_raag, self.mapping.get(g1, []))
                    image_g2 = RAAGElement(self.codomain_raag, self.mapping.get(g2, []))
                    if not self._do_elements_commute(image_g1, image_g2):
                        raise ValueError(f"Отображение не сохраняет коммутативность для {g1}, {g2}")

    # Проверяет, коммутируют ли два элемента
    def _do_elements_commute(self, elem1, elem2):
        combined1 = RAAGElement(self.codomain_raag, elem1.word + elem2.word)
        combined2 = RAAGElement(self.codomain_raag, elem2.word + elem1.word)
        return combined1.word == combined2.word  # Прямое сравнение слов после нормализации

    # Применяет гомоморфизм к элементу
    def apply(self, element):
        if element.raag != self.domain_raag:
            raise ValueError("Элемент из другой группы Артина.")
        image_word = []
        for g in element.word:
            base = g.replace("^-1", "")
            mapped = self.mapping.get(base, [])
            if g.endswith("^-1"):
                mapped = [self.codomain_raag.inverse(x) for x in reversed(mapped)]
            image_word.extend(mapped)
        return RAAGElement(self.codomain_raag, image_word)

# Кодирует текст в элемент RAAG
def encode_text(text, raag, alphabet_mapping):
    word = []
    for char in text.lower():
        if char not in alphabet_mapping:
            raise ValueError(f"Символ {char} не поддерживается в алфавите.")
        word.append(alphabet_mapping[char])
    return RAAGElement(raag, word)

# Декодирует элемент RAAG в текст, учитывая инверсии
def decode_text(element, alphabet_mapping):
    """
    Декодирует RAAGElement, удаляя образующие при появлении их инверсий.
    """
    reverse_mapping = {v: k for k, v in alphabet_mapping.items()}
    stack = []
    for g in element.word:
        base = g.replace("^-1", "")
        if base not in reverse_mapping:
            raise ValueError(f"Генератор {base} не соответствует алфавиту.")
        if g.endswith("^-1"):
            # Инверсия удаляет последний экземпляр базового генератора
            for i in range(len(stack) - 1, -1, -1):
                if stack[i] == base:
                    stack.pop(i)
                    break
        else:
            stack.append(base)
    return "".join(reverse_mapping[base] for base in stack if base in reverse_mapping)

# Декодирует образ в RAAG2, однозначно восстанавливая исходное слово
def decode_image(image, hom, alphabet_mapping):
    """
    Декодирует образ, сопоставляя подстроки с уникальными образами образующих.
    """
    reverse_mapping = {v: k for k, v in alphabet_mapping.items()}
    word = image.word[:]
    result = []
    i = 0
    while i < len(word):
        matched = False
        for g, mapped in hom.mapping.items():
            if i + len(mapped) <= len(word):
                if word[i:i + len(mapped)] == mapped:
                    if g in reverse_mapping.values():
                        result.append(reverse_mapping[g])
                        i += len(mapped)
                        matched = True
                        break
        if not matched:
            raise ValueError(f"Не удалось сопоставить подстроку начиная с позиции {i}")
    return "".join(result)

# Пример использования
if __name__ == "__main__":
    # Определяем RAAG1 и RAAG2
    raag1 = RAAG(["a", "b", "c", "d"], [("a", "b"), ("b", "c")])
    raag2 = RAAG(["x", "y", "z"], [("x", "y")])
    # Отображение алфавита
    alphabet_mapping = {"o": "a", "k": "b", "a": "c", "y": "d"}
    # Биективный гомоморфизм для однозначного декодирования
    mapping = {"a": ["x", "x"], "b": ["y", "y"], "c": ["z", "z"], "d": ["x", "y"]}
    hom = RAAGHomomorphism(raag1, raag2, mapping)
    text = "Okay"
    # Кодируем слово
    encoded = encode_text(text, raag1, alphabet_mapping)
    print(f"Закодированное слово '{text}': {encoded}")
    # Инверсия
    inv = encoded.inverse()
    print(f"Инверсия: {inv}")
    # Применяем гомоморфизм
    image = hom.apply(encoded)
    print(f"Образ в RAAG2: {image}")
    # Декодируем исходное слово
    decoded = decode_text(encoded, alphabet_mapping)
    print(f"Декодированное слово: {decoded}")
    # Декодируем образ
    decoded_image = decode_image(image, hom, alphabet_mapping)
    print(f"Декодированный образ: {decoded_image}")
