# Vector Database — decyzje projektowe

## Wybrana baza: Qdrant

Qdrant z algorytmem HNSW (Hierarchical Navigable Small World) do przyblizonego wyszukiwania najblizszych sasiadow (ANN).

---

## Schemat dokumentu

```json
{
  "id": 1,
  "vector": [0.1, 0.2, ...],
  "payload": {
    "raw": "oryginalny tekst ktory byl embedowany",
    "model": "text-embedding-3-small"
  }
}
```

### Pola

| Pole | Typ | Opis |
|------|-----|------|
| `id` | uint64 | unikalny identyfikator (liczba całkowita) |
| `vector` | float[] | embedding wygenerowany przez model |
| `payload.raw` | string | oryginalny tekst/dane ktore byly embedowane |
| `payload.model` | string | nazwa modelu ktory wygenenowal embedding |

> `payload` to narzucona przez Qdrant nazwa wrappera na metadane — nie ma znaczenia biznesowego.

---

## Flow wyszukiwania

```
1. Uzytkownik wpisuje fraze + wybiera model
2. Generujemy embedding frazy tym samym modelem
3. Qdrant: filter { model = "<wybrany model>" } + ANN search
4. Zwracamy top-K najblizszych dokumentow z polem raw
```

Filtrowanie po `model` przed wyszukiwaniem jest konieczne — przestrzenie wektorowe roznych modeli sa niekompatybilne (liczby z jednego modelu nie maja sensu porownane z liczbami z innego).

---

## Jak dziala HNSW (ANN)

Qdrant nie porownuje wektora zapytania z kazdym embedingiem w bazie (O(n)). Zamiast tego uzywa grafu wielowarstwowego:

```
Warstwa 2 (najrzadsza):    A ————————— F
Warstwa 1:             A — C — D — F — G
Warstwa 0 (wszystkie): A-B-C-D-E-F-G-H-I-J
```

Wyszukiwanie:
1. Wejdz od gory (mala liczba punktow) — grubo zlokalizuj Q
2. Zejdz do nizszej warstwy — uzyj poprzedniego wyniku jako start
3. Na warstwie 0 — przeszukaj lokalnie i zwroc top-K

Zasada: **greedy search** — zawsze idz do sasiada blizszego Q niz aktualny punkt.

Zamiast sprawdzic 1,000,000 wektorow sprawdza ~200-500. Accuracy = 95-99%.

### Miara podobienstwa

Cosine Similarity — standardowa dla embeddnigow tekstowych:

```
similarity = (A · B) / (|A| x |B|)
```

Wynik od -1 (przeciwne) do 1 (identyczne).

### Parametry HNSW

| Parametr | Opis |
|----------|------|
| `m` | liczba krawedzi na wezel (wiecej = dokladniej, wiecej RAM) |
| `ef_construct` | dokladnosc przy budowaniu grafu |
| `ef` | dokladnosc przy wyszukiwaniu (runtime tradeoff) |

---

## Przyklad odpowiedzi z Qdrant

```json
[
  { "id": 1, "score": 0.97, "payload": { "raw": "...", "model": "text-embedding-3-small" } },
  { "id": 2, "score": 0.91, "payload": { "raw": "...", "model": "text-embedding-3-small" } },
  { "id": 3, "score": 0.84, "payload": { "raw": "...", "model": "text-embedding-3-small" } }
]
```

`score` = cosine similarity — im wyzej tym bardziej podobne do zapytania.

---

## Alternatywy ktore byly rozwazone

| Baza | Powod odrzucenia |
|------|-----------------|
| pgvector | brak HNSW out-of-the-box, wymaga PostgreSQL |
| Pinecone | managed/platny, brak kontroli nad raw storage |
| Weaviate | bardziej rozbudowany niz potrzebujemy |
| Vertex AI Vector Search | sens tylko przy pelnym GCP managed stack |
