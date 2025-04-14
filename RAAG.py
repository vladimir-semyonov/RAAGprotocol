class RAAG:
    def __init__(self, generators, commuting_pairs):
        """
        Инициализирует правоугольную группу Артина.
        Args:
            generators: Список строк, представляющих образующие группы.
            commuting_pairs: Список кортежей, представляющих пары коммутирующих образующих.
        """
        self.generators = set(generators)
        self.commuting_pairs = set(tuple(sorted(pair)) for pair in commuting_pairs)
    def are_commuting(self, a, b):
        """
        Проверяет, коммутируют ли две образующие.
        Args:
            a: Первая образующая.
            b: Вторая образующая.
        Returns:
            True, если образующие коммутируют, False в противном случае.
        """
        return tuple(sorted((a, b))) in self.commuting_pairs or a == b

class RAAGElement:
    def __init__(self, raag, word):
        """
        Инициализирует элемент правоугольной группы Артина.
        Args:
            raag: Объект RAAG, к которому принадлежит элемент.
            word: Список строк, представляющих слово (последовательность образующих).
        """
        if not all(g in raag.generators for g in word):
            raise ValueError("Слово содержит недопустимые образующие.")
        self.raag = raag
        self.word = list(word)
        self.reduce()
    def __mul__(self, other):
        """
        Умножает два элемента группы Артина (конкатенация слов).
        Args:
            other: Другой элемент RAAGElement.
        Returns:
            Новый элемент RAAGElement, представляющий произведение.
        """
        if self.raag!= other.raag:
            raise ValueError("Элементы принадлежат разным группам Артина.")
        return RAAGElement(self.raag, self.word + other.word) 
    def reduce(self):
        """
        Редуцирует слово, применяя коммутационные соотношения.
        """
        changed = True
        while changed:
            changed = False
            new_word = 
            i = 0
            while i < len(self.word):
                if i + 1 < len(self.word) and self.raag.are_commuting(self.word[i], self.word[i+1]):
                    # Переставляем коммутирующие соседние образующие для дальнейшей редукции
                    if new_word and self.raag.are_commuting(new_word[-1], self.word[i+1]):
                        new_word.append(self.word[i+1])
                        new_word.append(self.word[i])
                        i += 2
                        changed = True
                    else:
                        new_word.append(self.word[i+1])
                        new_word.append(self.word[i])
                        i += 2
                        changed = True
                else:
                    new_word.append(self.word[i])
                    i += 1
            self.word = new_word 
    def __eq__(self, other):
        """
        Проверяет равенство двух элементов группы Артина.
        Args:
            other: Другой элемент RAAGElement.
        Returns:
            True, если элементы равны, False в противном случае.
        """
        if self.raag!= other.raag:
            return False
        temp1 = RAAGElement(self.raag, list(self.word))
        temp2 = RAAGElement(self.raag, list(other.word))
        return temp1.word == temp2.word 
    def __str__(self):
        return "".join(self.word)

class RAAGHomomorphism:
    def __init__(self, domain_raag, codomain_raag, mapping):
        """
        Инициализирует гомоморфизм между двумя правоугольными группами Артина.
        Args:
            domain_raag: Объект RAAG, представляющий область определения.
            codomain_raag: Объект RAAG, представляющий кообласть определения.
            mapping: Словарь, отображающий образующие области определения на слова в образующих кообласти определения.
        """
        self.domain_raag = domain_raag
        self.codomain_raag = codomain_raag
        self.mapping = mapping
        self._verify_homomorphism()
    def _verify_homomorphism(self):
        """
        Проверяет, что заданное отображение действительно является гомоморфизмом.
        Для каждой пары коммутирующих образующих в области определения,
        их образы в кообласти определения должны также коммутировать.
        """
        for g1 in self.domain_raag.generators:
            for g2 in self.domain_raag.generators:
                if self.domain_raag.are_commuting(g1, g2):
                    image_g1 = RAAGElement(self.codomain_raag, self.mapping.get(g1,))
                    image_g2 = RAAGElement(self.codomain_raag, self.mapping.get(g2,))
                    if not self._do_elements_commute(image_g1, image_g2):
                        raise ValueError(f"Отображение не сохраняет коммутационные соотношения для {g1} и {g2}.")
    def _do_elements_commute(self, elem1, elem2):
        """
        Проверяет, коммутируют ли два элемента в RAAG.
        В упрощенной реализации мы проверяем это, пытаясь переставить образующие в их словесных представлениях.
        Более надежный способ потребует канонической формы.
        """
        word1 = list(elem1.word)
        word2 = list(elem2.word)
        # Пробуем переместить word1 после word2
        temp_word1 = word2 + word1
        reduced1 = RAAGElement(self.codomain_raag, temp_word1)
        # Пробуем переместить word2 после word1
        temp_word2 = word1 + word2
        reduced2 = RAAGElement(self.codomain_raag, temp_word2)
        return reduced1 == reduced2
    def apply(self, element):
        """
        Применяет гомоморфизм к элементу области определения.
        Args:
            element: Элемент RAAGElement из области определения.
        Returns:
            Элемент RAAGElement из кообласти определения.
        """
        if element.raag!= self.domain_raag:
            raise ValueError("Элемент принадлежит другой группе Артина.")
        image_word = 
        for generator in element.word:
            image_word.extend(self.mapping.get(generator,))
        return RAAGElement(self.codomain_raag, image_word)


# Пример использования:
# Определяем две RAAG
generators1 = ["a", "b"]
commuting_pairs1 = [("a", "b")] # a и b коммутируют
raag1 = RAAG(generators1, commuting_pairs1)

generators2 = ["x", "y", "z"]
commuting_pairs2 = [("x", "y")] # x и y коммутируют
raag2 = RAAG(generators2, commuting_pairs2)

# Определяем гомоморфизм из raag1 в raag2
mapping = {"a": ["x", "z"], "b": ["y"]}
homomorphism = RAAGHomomorphism(raag1, raag2, mapping)

# Создаем элемент в raag1
element1 = RAAGElement(raag1, ["a", "b", "a"])
print(f"Элемент в RAAG1: {element1}")

# Применяем гомоморфизм
image_element = homomorphism.apply(element1)
print(f"Образ элемента в RAAG2: {image_element}")

# Протокол аутентификации (упрощенный пример):
# Алиса создает свои RAAG и гомоморфизм (секретный ключ)
alice_raag1 = RAAG(["p", "q"], [("p", "q")])
alice_raag2 = RAAG(["r", "s", "t"], [("r", "s")])
alice_mapping = {"p": ["r", "t"], "q": ["s"]}
alice_homomorphism = RAAGHomomorphism(alice_raag1, alice_raag2, alice_mapping)

# Боб отправляет запрос (случайный элемент из alice_raag1)
bob_query = RAAGElement(alice_raag1, ["p", "q", "p"])
print(f"\nЗапрос Боба: {bob_query}")

# Алиса вычисляет ответ
alice_response = alice_homomorphism.apply(bob_query)
print(f"Ответ Алисы: {alice_response}")

# В реальном сценарии Боб должен иметь способ проверить, действительно ли alice_response
# является образом bob_query при действии секретного гомоморфизма Алисы.
# Это может потребовать более сложного протокола с использованием дополнительных раундов
# или публикации некоторой открытой информации об гомоморфизме.
