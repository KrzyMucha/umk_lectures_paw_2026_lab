#!/usr/bin/env python3
"""
Generuje HTML wyglądający jak chat z historii rozmowy.
Otwórz w przeglądarce i użyj Cmd+P → Save as PDF.
"""

CONVERSATION = [
    ("user", "Kontynuujemy poprzednią sesję. Mamy już: 1000 produktów NBA z opisami w DB, 1000 embeddingów (768-dim) przez Ollama nomic-embed-text, endpointy GET /sport-products. Teraz tworzymy /sport-products/search z osobnym plikiem OllamaClient.scala."),
    ("assistant", "Gotowe. Nowy plik OllamaClient.scala — 21 linii, cały Ollama logic w jednym miejscu.\n\nNowy endpoint:\nGET /sport-products/search?q=LeBron+playoff+jersey&limit=5\n\nUruchomienie:\n./scripts/products/local-products-service.sh\ncurl \"http://localhost:8081/sport-products/search?q=LeBron+playoff+jersey\""),
    ("user", "Jak powinienem wpisywać zapytania?"),
    ("assistant", "Naturalnym językiem, tak jak byś opisał produkt:\n\ncurl \"http://localhost:8081/sport-products/search?q=LeBron+playoff+jersey\"\ncurl \"http://localhost:8081/sport-products/search?q=basketball+shoes+Nike\"\ncurl \"http://localhost:8081/sport-products/search?q=Stephen+Curry+Warriors&limit=3\"\n\nWyszukiwanie semantyczne działa na podobieństwie wektorów — zwraca produkty, których opis znaczeniowo pasuje do zapytania, nie muszą zawierać dokładnych słów."),
    ("user", "Ale jak wpisuję 'I want Barkley' to nie znajduje produktów Barkleya."),
    ("assistant", "Produkty Barkleya są w DB (sprawdziłem). Problem leży gdzie indziej — prawdopodobnie serwis nie startuje.\n\nSprawdziłem: port 8081 był już zajęty — serwis był już uruchomiony.\n\nWyszukiwanie po prostu nie zwraca Barkleya bo to wyszukiwanie semantyczne oparte na opisach. Model nomic-embed-text nie łączy słowa 'Barkley' z konkretnymi produktami.\n\nDo wyszukiwania po nazwisku użyj zwykłego endpointu:\ncurl \"http://localhost:8081/sport-products?name=Barkley\"\n\nSemantic search działa najlepiej przy opisach jak:\ncurl \"...?q=aggressive+rebounder+power+forward+Phoenix\""),
    ("user", "Ale nie mam żadnych błędów, mam po prostu inne produkty."),
    ("assistant", "To jest poprawne zachowanie wyszukiwania semantycznego — model nie wie że 'Barkley' to koszykarz, bo to imię własne.\n\nEmbedding dla produktu Barkleya zawierał 'player: Charles Barkley' — więc zapytanie 'Charles Barkley' powinno zadziałać:\n\ncurl -s \"http://localhost:8081/sport-products/search?q=Charles+Barkley&limit=5\"\n\nSam 'Barkley' to za mało — model dopasowuje pełny kontekst semantyczny."),
    ("user", "Może wektor powinien zawierać opis i tytuł?"),
    ("assistant", "Tak, ma sens. Zmieniłem generate-embeddings.py — format tekstu do embeddingu to teraz tylko:\nnazwa | opis\n\nPo przeliczeniu embeddingi będą bardziej semantycznie spójne."),
    ("user", "I może inne parametry — aby można było powiedzieć że chcę tani."),
    ("assistant", "Ceny od ~$20 do ~$300, średnia ~$112. Dodałem do tekstu embeddingu opis kategorii cenowej:\n\n• < $40 → 'cheap budget affordable low price'\n• $40-90 → 'affordable mid-range price'\n• $90-180 → 'mid-range price'\n• > $180 → 'expensive premium luxury high price'\n\nPo przeliczeniu zadziałają zapytania:\n?q=cheap+basketball+shoes\n?q=affordable+jersey\n?q=expensive+premium+collectible"),
    ("user", "Dodaj wszystkie parametry — datę meczu, punkty itp."),
    ("assistant", "Zaktualizowałem format tekstu embeddingu do pełnego:\nnazwa | opis | cena (label) | player: X | opponent: X | game date: X | N points M rebounds A assists S steals B blocks\n\nTeraz zadziałają zapytania jak:\n?q=Charles+Barkley\n?q=40+points+game\n?q=high+assists+playmaker\n?q=1998+finals+jersey"),
    ("user", "Wszystkie produkty mają już embeddingi."),
    ("assistant", "Wszystkie 1000 gotowe. Możesz testować:\ncurl -s \"http://localhost:8081/sport-products/search?q=Charles+Barkley\" | python3 -m json.tool | grep -E '\"name\"|\"player\"'"),
    ("user", "Kurde słabo — robię MJ i dostaję Kobe Bryant."),
    ("assistant", "To normalne — nomic-embed-text nie wie że 'MJ' = Michael Jordan. Spróbuj pełnego imienia:\ncurl -s \"http://localhost:8081/sport-products/search?q=Michael+Jordan&limit=1\"\n\nEmbeddingi były generowane z tekstem 'player: Michael Jordan', więc 'MJ' semantycznie trafia w środowisko koszykówki lat 90. i zwraca podobnych zawodników (Kobe też jest 'championship, legacy, clutch'). To ograniczenie modelu lokalnego — nie rozumie skrótów i pseudonimów."),
    ("user", "Ok, więc teraz zróbmy to samo z jakimś darmowym modelem zdalnym."),
    ("assistant", "Klucz działa! Model to gemini-embedding-001 (3072 wymiarów).\n\nPonieważ pgvector HNSW ma limit 2000 wymiarów, użyjemy outputDimensionality=768 — Gemini wspiera MRL więc jakość nadal dobra.\n\nPlan:\n1. Nowa kolumna embedding_gemini vector(768) w DB\n2. Skrypt generate-embeddings-gemini.py\n3. GeminiClient.scala (osobny plik)\n4. Parametr ?model=gemini lub ?model=ollama w endpoincie search"),
    ("user", "Dodaj kolejną kolumnę, aby można było korzystać z wielu modeli. Dodaj kolejnego klienta. Dodaj kolejny skrypt dla nowej kolumny."),
    ("assistant", "Zrobione i skompilowane!\n\nNowe pliki:\n• GeminiClient.scala — używa Java stdlib HttpClient, outputDimensionality=768\n• generate-embeddings-gemini.py — zapisuje do kolumny embedding_gemini\n\nZmiany w istniejących plikach:\n• SportProductRepository — nowa metoda findSimilarGemini()\n• SportProductController — parametr model: String\n• Routes — dodany ?model=gemini parametr\n• Main.scala — GeminiClient tworzony z GEMINI_API_KEY\n\nUżycie:\ncurl \"...?q=Michael+Jordan&model=gemini&limit=3\"  ← Gemini\ncurl \"...?q=Michael+Jordan&model=ollama&limit=3\"  ← Ollama"),
    ("user", "Ok, zindeksowałem produkty — 997/1000 gotowe."),
    ("assistant", "Przetestuj porównanie modeli:\ncurl -s \".../search?q=Michael+Jordan&model=gemini&limit=3\" | grep -E '\"name\"|\"player\"'\ncurl -s \".../search?q=Michael+Jordan&model=ollama&limit=3\" | grep -E '\"name\"|\"player\"'"),
    ("user", "Mam w przeglądarce error: 'gemini embedding failed'"),
    ("assistant", "Port 8081 był zajęty — stary proces bez GEMINI_API_KEY. Zatrzymałem stary proces. Uruchom serwis ponownie:\n./scripts/products/local-products-service.sh"),
    ("user", "To samo — error: 'gemini embedding failed'. Zrób tak aby serwis zwracał wszystkie szczegóły błędów."),
    ("assistant", "Zaktualizowałem GeminiClient żeby rzucał wyjątek z pełną treścią odpowiedzi HTTP, i SportProductController żeby zwracał szczegóły przez .attempt. Teraz dostaniesz dokładny błąd od Gemini API."),
    ("user", "error: { code: 400, message: 'API key not valid. Please pass a valid API key.' }"),
    ("assistant", "Klucz może być już nieważny — Google automatycznie unieważnia klucze API gdy wykryje je w plikach/rozmowach.\n\nWygeneruj nowy na aistudio.google.com/apikey i zaktualizuj .env."),
    ("user", "Nie sądzę że to jest to — zrób tak aby wypisywał klucz w błędzie, zobaczymy czy ładuje poprawnie."),
    ("assistant", "Klucz w błędzie to key=gsk_ltzI... — to klucz Groq, nie Gemini!\n\nPrawdopodobnie masz w środowisku zmienną GEMINI_API_KEY ustawioną na klucz Groq z poprzedniej sesji. Sprawdziłem .env — plik był pusty (nie zawierał GEMINI_API_KEY). Klucz wpisany był do innego miejsca lub niezapisany."),
    ("user", "Czaję, możliwe że plik był otwarty w terminalu ale się nie zapisał."),
    ("assistant", "Dodaj klucz ręcznie:\necho \"GEMINI_API_KEY=AIza...\" >> services/products-service/.env\ncat services/products-service/.env  # weryfikacja\nPotem zrestartuj serwis."),
]

HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Semantic Search — Historia rozmowy</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    min-height: 100vh;
  }}
  .header {{
    background: linear-gradient(135deg, #16213e, #0f3460);
    padding: 24px 32px;
    border-bottom: 2px solid #e94560;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .header h1 {{
    font-size: 1.5rem;
    color: #e94560;
    margin-bottom: 4px;
  }}
  .header p {{
    font-size: 0.85rem;
    color: #a0a0b0;
  }}
  .subtitle-tags {{
    display: flex;
    gap: 8px;
    margin-top: 10px;
    flex-wrap: wrap;
  }}
  .tag {{
    background: #0f3460;
    border: 1px solid #e94560;
    color: #e94560;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
  }}
  .chat-container {{
    max-width: 960px;
    margin: 0 auto;
    padding: 32px 24px;
  }}
  .message {{
    display: flex;
    margin-bottom: 20px;
    gap: 12px;
    animation: fadeIn 0.3s ease;
  }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .message.user {{
    flex-direction: row-reverse;
  }}
  .avatar {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    font-weight: bold;
    flex-shrink: 0;
    margin-top: 2px;
  }}
  .message.user .avatar {{
    background: linear-gradient(135deg, #e94560, #c73652);
    color: white;
  }}
  .message.assistant .avatar {{
    background: linear-gradient(135deg, #0f3460, #16213e);
    border: 2px solid #e94560;
    color: #e94560;
  }}
  .bubble {{
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 16px;
    line-height: 1.6;
    font-size: 0.92rem;
    white-space: pre-wrap;
  }}
  .message.user .bubble {{
    background: linear-gradient(135deg, #e94560, #c73652);
    color: white;
    border-bottom-right-radius: 4px;
  }}
  .message.assistant .bubble {{
    background: #16213e;
    border: 1px solid #2a2a4e;
    color: #d0d0e0;
    border-bottom-left-radius: 4px;
  }}
  .bubble code, .bubble pre {{
    background: #0d0d1a;
    border: 1px solid #2a2a4e;
    border-radius: 6px;
    padding: 2px 6px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.85em;
    color: #7ec8e3;
  }}
  .bubble pre {{
    padding: 10px 12px;
    overflow-x: auto;
    margin: 6px 0;
    display: block;
    white-space: pre;
  }}
  .label {{
    font-size: 0.72rem;
    color: #606080;
    margin-bottom: 4px;
    padding: 0 4px;
  }}
  .message.user .label {{
    text-align: right;
  }}
  .message-wrap {{
    display: flex;
    flex-direction: column;
    width: 100%;
  }}
  .message.user .message-wrap {{
    align-items: flex-end;
  }}
  .section-divider {{
    text-align: center;
    margin: 32px 0 16px;
    position: relative;
  }}
  .section-divider::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: #2a2a4e;
  }}
  .section-divider span {{
    background: #1a1a2e;
    padding: 0 16px;
    position: relative;
    color: #e94560;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .footer {{
    text-align: center;
    padding: 32px;
    color: #404060;
    font-size: 0.8rem;
    border-top: 1px solid #2a2a4e;
    margin-top: 40px;
  }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    .header {{ background: #f0f0f0; border-bottom: 2px solid #e94560; position: static; }}
    .header h1 {{ color: #e94560; }}
    .header p, .label {{ color: #666; }}
    .message.assistant .bubble {{ background: #f5f5f5; border: 1px solid #ddd; color: #222; }}
    .message.user .bubble {{ background: #e94560; color: white; }}
    .bubble code, .bubble pre {{ background: #f0f0f0; border: 1px solid #ccc; color: #0066cc; }}
    .tag {{ border-color: #e94560; color: #e94560; background: #fff; }}
    .section-divider::before {{ background: #ccc; }}
    .section-divider span {{ background: #fff; color: #e94560; }}
    .footer {{ color: #999; border-top: 1px solid #ccc; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>🔍 Semantic Search — Scala + pgvector + Ollama + Gemini</h1>
  <p>Historia implementacji wyszukiwania semantycznego produktów NBA | PAW 2026</p>
  <div class="subtitle-tags">
    <span class="tag">Scala 3.6.4</span>
    <span class="tag">http4s</span>
    <span class="tag">pgvector</span>
    <span class="tag">Ollama nomic-embed-text</span>
    <span class="tag">Gemini Embedding</span>
    <span class="tag">PostgreSQL 16</span>
    <span class="tag">1000 produktów NBA</span>
  </div>
</div>
<div class="chat-container">
{messages}
</div>
<div class="footer">
  PAW 2026 · UMK · Implementacja semantic search w mikroserwisie Scala
</div>
</body>
</html>
"""

SECTIONS = {
    0:  "Implementacja /sport-products/search",
    4:  "Testowanie — jak wpisywać zapytania?",
    7:  "Poprawa jakości embeddingów",
    12: "Porównanie: MJ vs Kobe — ograniczenia modelu lokalnego",
    13: "Rozszerzenie: Gemini API jako drugi model",
    14: "Wiele modeli — dwie kolumny w DB",
    16: "Debugowanie — klucz API",
}


def format_text(text):
    import html
    text = html.escape(text)
    lines = text.split("\n")
    result = []
    in_code = False
    code_lines = []
    for line in lines:
        stripped = line.lstrip()
        is_code = stripped.startswith("curl ") or stripped.startswith("python3 ") or \
                  stripped.startswith("./") or stripped.startswith("docker ") or \
                  stripped.startswith("sbt ") or stripped.startswith("?q=") or \
                  stripped.startswith("GET ") or stripped.startswith("POST ") or \
                  stripped.startswith("•")
        if is_code and not in_code:
            in_code = True
            code_lines = [stripped]
        elif is_code and in_code:
            code_lines.append(stripped)
        elif not is_code and in_code:
            result.append(f"<pre>{chr(10).join(code_lines)}</pre>")
            code_lines = []
            in_code = False
            result.append(line)
        else:
            result.append(line)
    if in_code:
        result.append(f"<pre>{chr(10).join(code_lines)}</pre>")
    return "\n".join(result)


def build_html():
    messages_html = []
    for i, (role, text) in enumerate(CONVERSATION):
        if i in SECTIONS:
            messages_html.append(f'<div class="section-divider"><span>{SECTIONS[i]}</span></div>')

        label = "Ty" if role == "user" else "GitHub Copilot"
        avatar = "Ty" if role == "user" else "AI"
        formatted = format_text(text)

        messages_html.append(f"""
  <div class="message {role}">
    <div class="avatar">{avatar}</div>
    <div class="message-wrap">
      <div class="label">{label}</div>
      <div class="bubble">{formatted}</div>
    </div>
  </div>""")

    return HTML.format(messages="\n".join(messages_html))


if __name__ == "__main__":
    import os
    out_path = os.path.join(os.path.dirname(__file__), "chat-semantic-search.html")
    html_content = build_html()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Zapisano: {out_path}")
    print("Otwórz w przeglądarce i użyj Cmd+P → Save as PDF")
    # Spróbuj otworzyć w przeglądarce
    import subprocess
    subprocess.run(["open", out_path], check=False)
