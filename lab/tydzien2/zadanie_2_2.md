# Zadanie 2.2: CI/CD Pipeline i Code Review

## Cel
Skonfigurować automatyczny deployment przez GitHub Actions oraz nauczyć się procesu code review.

## Czas
~40 minut

## Wymagania wstępne
- Ukończone zadanie 2.1 (Hello Team)
- Dostęp do repo GitHub (jako collaborator)

---

## Część 1: Zrozumienie pipeline (~10 min)

### Jak działa nasz pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Branch    │ ──▶ │ Pull Request│ ──▶ │   Review    │ ──▶ │   Merge     │
│  feature/*  │     │   do main   │     │  + Approve  │     │  → Deploy   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                                       │
                           ▼                                       ▼
                    GitHub Actions:                         GitHub Actions:
                    - terraform fmt                         - terraform apply
                    - terraform plan                        - deploy!
```

### Co robi GitHub Actions?

**Na Pull Request:**
1. Sprawdza formatowanie kodu (`terraform fmt`)
2. Pokazuje plan zmian (`terraform plan`)
3. Nie deployuje jeszcze!

**Po merge do main:**
1. Wykonuje deployment (`terraform apply`)
2. Zmiany są na produkcji

---

## Część 2: Praca z branchami (~10 min)

### Krok 1: Utwórz branch
```bash
# Upewnij się, że jesteś na aktualnym main
git checkout main
git pull origin main

# Utwórz nowy branch
git checkout -b feature/update-hello-{imie}
```

### Krok 2: Zrób zmianę
Edytuj swój plik `services/hello-team/functions/{imie}.tf`:
- Zmień opis funkcji
- Lub dodaj nowy label

Przykład:
```hcl
labels = {
  team    = "zespol-1"
  author  = "anna"
  version = "2"          # <- dodaj to
}
```

### Krok 3: Commit i push
```bash
git add .
git commit -m "Update hello-{imie}: add version label"
git push origin feature/update-hello-{imie}
```

---

## Część 3: Pull Request (~10 min)

### Krok 1: Otwórz PR
1. Wejdź na GitHub → repo → zakładka **Pull requests**
2. Kliknij **New pull request**
3. Wybierz:
   - base: `main`
   - compare: `feature/update-hello-{imie}`
4. Kliknij **Create pull request**

### Krok 2: Wypełnij opis PR
```markdown
## Co zmienia ten PR?
- Dodaje label `version` do funkcji hello-{imie}

## Checklist
- [ ] Kod się kompiluje
- [ ] Terraform plan wygląda OK
- [ ] Przetestowałem lokalnie
```

### Krok 3: Poczekaj na CI
- GitHub Actions automatycznie uruchomi checks
- Zobaczysz status: pending → success/failure
- Kliknij "Details" żeby zobaczyć logi
- Sprawdź output `terraform plan` - czy zmiany są zgodne z oczekiwaniami?

---

## Część 4: Code Review (~10 min)

### Jako reviewer (recenzent)

1. Wejdź w PR kolegi/koleżanki z zespołu
2. Zakładka **Files changed** - zobacz zmiany
3. Kliknij na linię kodu → dodaj komentarz
4. Na górze kliknij **Review changes**
5. Wybierz:
   - **Comment** - tylko komentarz
   - **Approve** - zatwierdzam ✅
   - **Request changes** - wymaga poprawek ❌

### Przykładowe komentarze review

**Dobre komentarze:**
- "Czy ten label jest potrzebny?"
- "Może warto dodać też label `env = dev`?"
- "LGTM! (Looks Good To Me)"

**Złe komentarze:**
- "OK" (niekonkretne)
- "Źle" (bez wyjaśnienia)

### Jako autor PR

1. Odpowiadaj na komentarze
2. Jeśli trzeba poprawić:
   ```bash
   # Na tym samym branchu
   git add .
   git commit -m "Address review comments"
   git push
   ```
3. PR automatycznie się zaktualizuje
4. Poproś o ponowny review

---

## Część 5: Merge i Deploy

### Krok 1: Merge PR
Po uzyskaniu approval:
1. Kliknij **Merge pull request**
2. Wybierz **Squash and merge** (czysta historia)
3. Potwierdź

### Krok 2: Obserwuj deployment
1. Zakładka **Actions** w repo
2. Znajdź workflow uruchomiony po merge
3. Obserwuj `terraform apply`
4. Po zakończeniu - Twoja zmiana jest na produkcji!

### Krok 3: Zweryfikuj
1. Otwórz URL swojej funkcji
2. Sprawdź czy działa
3. W GCP Console → Cloud Functions → Twoja funkcja → Labels

---

## Checkpoint

- [ ] Utworzyłem branch `feature/*`
- [ ] Otworzyłem Pull Request
- [ ] CI (GitHub Actions) przeszło
- [ ] Ktoś zrobił review mojego PR
- [ ] Zrobiłem review czyjego PR
- [ ] PR został zmergowany
- [ ] Deployment się wykonał
- [ ] Zmiany są widoczne w GCP

---

## Zasady Code Review w naszym projekcie

### Kto reviewuje kogo?
- Zmiany w `services/zespol-X/*` → reviewuje ktoś z zespołu X
- Zmiany w `shared/*` lub `infrastructure/*` → reviewuje ktoś z innego zespołu

### Wymagania przed merge
1. Minimum 1 approval
2. CI musi przejść (zielony check)
3. Brak unresolved comments

### Git workflow
```
main (produkcja)
 │
 ├── feature/add-user-api      ← nowa funkcjonalność
 ├── feature/update-hello-anna ← update
 ├── fix/cors-error            ← bugfix
 └── ...
```

---

## Rozwiązywanie problemów

### "CI failed - terraform fmt"
Kod nie jest sformatowany:
```bash
terraform fmt -recursive
git add .
git commit -m "Format terraform code"
git push
```

### "CI failed - terraform plan"
Błąd w kodzie Terraform. Sprawdź logi w GitHub Actions.

### "Merge conflicts"
Twój branch jest nieaktualny:
```bash
git checkout main
git pull
git checkout feature/twoj-branch
git merge main
# Rozwiąż konflikty
git add .
git commit -m "Resolve merge conflicts"
git push
```

### "Nie mogę pushować do main"
Dobrze! Main jest chroniony. Musisz użyć Pull Request.

---

## Pytania kontrolne

1. Dlaczego nie pushujemy bezpośrednio do `main`?
2. Co robi `terraform plan` vs `terraform apply`?
3. Po co jest code review?
4. Kiedy GitHub Actions wykonuje deployment?
