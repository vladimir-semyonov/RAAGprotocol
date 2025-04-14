class RAAG:
    def __init__(self, generators, commuting_pairs):
        self.generators = set(generators)
        self.commuting_pairs = set(tuple(sorted(pair)) for pair in commuting_pairs)

        # Поддержка инверсий — создаем множество допустимых образующих с инверсией
        self.extended_generators = self.generators.union(
            {g + "^-1" for g in self.generators}
        )

    def are_commuting(self, a, b):
        # Убираем инверсии для проверки коммутативности
        a_base = a.replace("^-1", "")
        b_base = b.replace("^-1", "")
        return tuple(sorted((a_base, b_base))) in self.commuting_pairs or a_base == b_base

    def inverse(self, g):
        return g[:-3] if g.endswith("^-1") else g + "^-1"


class RAAGElement:
    def __init__(self, raag, word):
        if not all(g in raag.extended_generators for g in word):
            raise ValueError("Слово содержит недопустимые образующие или инверсии.")
        self.raag = raag
        self.word = list(word)
        self.reduce()

    def __mul__(self, other):
        if self.raag != other.raag:
            raise ValueError("Элементы принадлежат разным группам Артина.")
        return RAAGElement(self.raag, self.word + other.word)

    def reduce(self):
        """
        Упрощает слово:
        - удаляет g g^-1 и g^-1 g
        - переставляет коммутирующие элементы
        - приводит к нормальной форме
        """
        changed = True
        while changed:
            changed = False
            i = 0
            new_word = []
            while i < len(self.word):
                if i + 1 < len(self.word):
                    a, b = self.word[i], self.word[i + 1]
                    # Упрощение: g g^-1 или g^-1 g -> e
                    if self.raag.inverse(a) == b:
                        i += 2
                        changed = True
                        continue
                    # Перестановка коммутирующих элементов
                    if self.raag.are_commuting(a, b) and a > b:
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

    def __eq__(self, other):
        if self.raag != other.raag:
            return False
        return self.word == other.word

    def __str__(self):
        return " ".join(self.word)

    def inverse(self):
        # Инвертируем порядок и каждый символ
        inv_word = [self.raag.inverse(g) for g in reversed(self.word)]
        return RAAGElement(self.raag, inv_word)


class RAAGHomomorphism:
    def __init__(self, domain_raag, codomain_raag, mapping):
        """
        mapping: {"a": ["x", "z"], "b": ["y"], ...}
        """
        self.domain_raag = domain_raag
        self.codomain_raag = codomain_raag
        self.mapping = mapping
        self._verify_homomorphism()

    def _verify_homomorphism(self):
        for g1 in self.domain_raag.generators:
            for g2 in self.domain_raag.generators:
                if self.domain_raag.are_commuting(g1, g2):
                    image_g1 = RAAGElement(self.codomain_raag, self.mapping.get(g1, []))
                    image_g2 = RAAGElement(self.codomain_raag, self.mapping.get(g2, []))
                    if not self._do_elements_commute(image_g1, image_g2):
                        raise ValueError(
                            f"Отображение не сохраняет коммутативность для {g1}, {g2}")   

    def _do_elements_commute(self, elem1, elem2):
        combined1 = RAAGElement(self.codomain_raag, elem1.word + elem2.word)
        combined2 = RAAGElement(self.codomain_raag, elem2.word + elem1.word)
        return combined1 == combined2

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


# === Пример использования ===
if __name__ == "__main__":
    # Определяем RAAG
    raag1 = RAAG(["a", "b"], [("a", "b")])
    raag2 = RAAG(["x", "y", "z"], [("x", "y")])

    # Гомоморфизм
    mapping = {"a": ["x", "z"], "b": ["y"]}
    hom = RAAGHomomorphism(raag1, raag2, mapping)

    # Элемент в raag1
    el1 = RAAGElement(raag1, ["a", "b", "a^-1", "b^-1"])
    print("Элемент в RAAG1:", el1)

    # Инверсия и нормализация
    inv = el1.inverse()
    print("Инверсия:", inv)

    # Применение гомоморфизма
    image = hom.apply(el1)
    print("Образ в RAAG2:", image)
