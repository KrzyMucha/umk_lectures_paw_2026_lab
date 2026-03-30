# Zadanie 2.0: Setup środowiska

## Cel
Przygotować środowisko deweloperskie do pracy z GCP, Terraform, TypeScript i Docker.

## Czas
Zadanie domowe (przed Lab 2) + ~15 min weryfikacja na zajęciach

---

## Wymagane oprogramowanie

### 1. Visual Studio Code

**Instalacja:**
1. Pobierz: https://code.visualstudio.com/
2. Zainstaluj (domyślne opcje)

**Wymagane rozszerzenia:**
Otwórz VS Code → Extensions (Ctrl+Shift+X) → wyszukaj i zainstaluj:

| Rozszerzenie | ID | Do czego |
|--------------|-----|----------|
| HashiCorp Terraform | `hashicorp.terraform` | Podświetlanie, autouzupełnianie Terraform |
| Cloud Code | `googlecloudtools.cloudcode` | Integracja z GCP |
| ESLint | `dbaeumer.vscode-eslint` | Linter dla JavaScript/TypeScript |
| Prettier | `esbenp.prettier-vscode` | Formatowanie kodu |
| GitLens | `eamodio.gitlens` | Lepsza integracja z Git |

**AI Assistant (wymagane):**
| Rozszerzenie | ID | Do czego |
|--------------|-----|----------|
| GitHub Copilot | `github.copilot` | AI assistant (free dla studentów) |
| GitHub Copilot Chat | `github.copilot-chat` | Chat z AI w VS Code |

**Opcjonalne (przydatne):**
| Rozszerzenie | ID | Do czego |
|--------------|-----|----------|
| Thunder Client | `rangav.vscode-thunder-client` | Testowanie API (jak Postman) |
| Error Lens | `usernamehw.errorlens` | Pokazuje błędy inline |

**Weryfikacja:**
- Otwórz VS Code
- Extensions → Installed → sprawdź czy wszystkie są zainstalowane

---

### 2. GitHub Education + GitHub Copilot (WYMAGANE)

GitHub Copilot to asystent AI, który pomaga pisać kod. Dla studentów jest **darmowy**.

**Krok 1: Rejestracja w GitHub Education**
1. Wejdź: https://education.github.com/pack
2. Kliknij "Get your pack"
3. Zaloguj się na GitHub (lub utwórz konto)
4. Wybierz "Student"
5. Zweryfikuj status studenta:
   - Użyj emaila uczelnianego: `@stud.umk.pl`
   - LUB prześlij zdjęcie legitymacji
6. Czekaj na weryfikację (1-7 dni)

**Krok 2: Aktywacja Copilot**
1. Po zatwierdzeniu wejdź: https://github.com/settings/copilot
2. Kliknij "Enable GitHub Copilot"
3. Wybierz ustawienia (domyślne OK)

**Krok 3: Instalacja w VS Code**
1. VS Code → Extensions
2. Wyszukaj "GitHub Copilot" → Install
3. Wyszukaj "GitHub Copilot Chat" → Install
4. Zaloguj się do GitHub (VS Code poprosi)

**Weryfikacja:**
- Otwórz plik `.ts` lub `.tf`
- Zacznij pisać - Copilot powinien podpowiadać (szary tekst)
- Naciśnij Tab aby zaakceptować podpowiedź
- Ctrl+I (lub Cmd+I) otwiera Copilot Chat

**Jeśli weryfikacja GitHub Education trwa za długo:**
Zainstaluj tymczasowo **Codeium** (darmowy, bez weryfikacji):
- VS Code → Extensions → "Codeium" → Install

---

### 3. Node.js (JavaScript runtime)

**Instalacja:**
1. Pobierz **LTS** (Long Term Support): https://nodejs.org/
2. Zainstaluj (domyślne opcje)
3. Restart terminala

**Weryfikacja:**
```bash
node --version
# Oczekiwane: v20.x.x lub nowsze

npm --version
# Oczekiwane: 10.x.x lub nowsze
```

---

### 4. Git

**Instalacja:**
- Windows: https://git-scm.com/download/windows
- macOS: `xcode-select --install` lub https://git-scm.com/download/mac
- Linux: `sudo apt install git` lub `sudo dnf install git`

**Konfiguracja (jednorazowo):**
```bash
git config --global user.name "Twoje Imię Nazwisko"
git config --global user.email "twoj.email@gmail.com"
```

**Weryfikacja:**
```bash
git --version
# Oczekiwane: git version 2.x.x
```

---

### 5. Terraform

**Instalacja:**

**Windows:**
1. Pobierz: https://developer.hashicorp.com/terraform/install
2. Rozpakuj do `C:\terraform\`
3. Dodaj do PATH:
   - Win+R → `sysdm.cpl` → Advanced → Environment Variables
   - Path → Edit → New → `C:\terraform`
4. Restart terminala

**macOS (Homebrew):**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux (Ubuntu/Debian):**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Weryfikacja:**
```bash
terraform --version
# Oczekiwane: Terraform v1.x.x
```

---

### 6. Google Cloud CLI (gcloud)

**Instalacja:**
1. Pobierz: https://cloud.google.com/sdk/docs/install
2. Uruchom installer
3. Restart terminala

**Weryfikacja:**
```bash
gcloud --version
# Oczekiwane: Google Cloud SDK x.x.x
```

**Konfiguracja (na Lab 2):**
```bash
# Logowanie (otworzy przeglądarkę)
gcloud auth login

# Ustawienie projektu
gcloud config set project paw-2026

# Weryfikacja
gcloud config list
```

---

### 7. Docker Desktop

**Instalacja:**

**Windows / macOS:**
1. Pobierz: https://www.docker.com/products/docker-desktop/
2. Zainstaluj
3. Uruchom Docker Desktop
4. Poczekaj aż ikona Docker w zasobniku/menu bar przestanie się animować

**macOS (Homebrew):**
```bash
brew install --cask docker
```
Potem uruchom aplikację Docker z Launchpad.

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Wyloguj i zaloguj ponownie
```

**Weryfikacja:**
```bash
docker --version
# Oczekiwane: Docker version 24.x.x lub nowsze

docker compose version
# Oczekiwane: Docker Compose version v2.x.x
```

---

## Checkpoint - Lista kontrolna

### Komendy w terminalu
Uruchom i sprawdź czy wszystko działa:

```bash
# VS Code
code --version

# Node.js
node --version
npm --version

# Git
git --version

# Terraform
terraform --version

# Google Cloud CLI
gcloud --version

# Docker
docker --version
docker compose version
```

**Wszystkie komendy powinny zwrócić numery wersji (nie błędy).**

### GitHub Copilot
- [ ] Mam konto GitHub
- [ ] Złożyłem wniosek do GitHub Education
- [ ] Zainstalowałem rozszerzenie GitHub Copilot w VS Code
- [ ] Copilot podpowiada kod (lub mam Codeium jako backup)

---

## VS Code - sprawdzenie rozszerzeń

1. Otwórz VS Code
2. Utwórz plik `test.tf`:
```hcl
resource "google_storage_bucket" "test" {
  name     = "test-bucket"
  location = "EU"
}
```
3. Sprawdź czy:
   - Kod jest kolorowany (syntax highlighting)
   - Po wpisaniu `resource "` pojawiają się podpowiedzi

4. Utwórz plik `test.ts`:
```typescript
const hello: string = "world";
console.log(hello);
```
5. Sprawdź czy TypeScript jest rozpoznawany

---

## Rozwiązywanie problemów

### "terraform: command not found"
- Windows: sprawdź czy dodałeś folder do PATH
- Restart terminala po instalacji

### "gcloud: command not found"
- Restart terminala
- Sprawdź czy installer się zakończył poprawnie

### VS Code nie pokazuje podpowiedzi dla Terraform
- Upewnij się, że rozszerzenie HashiCorp Terraform jest zainstalowane
- Reload VS Code (Ctrl+Shift+P → "Reload Window")

### "npm: command not found" (mimo że Node.js zainstalowany)
- Windows: użyj "Node.js command prompt" lub restart komputera
- Sprawdź czy Node.js jest w PATH

### "docker: command not found" lub "Cannot connect to Docker daemon"
- Upewnij się, że Docker Desktop jest uruchomiony (ikona w zasobniku/menu bar)
- Windows/macOS: uruchom aplikację Docker Desktop
- Linux: `sudo systemctl start docker`

---

## Następne kroki

Po ukończeniu tego zadania będziesz gotowy do:
1. Logowania do GCP (Lab 2)
2. Tworzenia Cloud Functions
3. Pisania kodu Terraform
4. Pracy z Git i GitHub
5. Uruchamiania aplikacji w kontenerach Docker (Lab 3+)
