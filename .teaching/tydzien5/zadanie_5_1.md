# Zadanie 5.1: Cloud SQL

Dodaj bazę danych PostgreSQL do projektu. Dev i prod mają osobne bazy.

## Co zrobić

Rozszerz konfigurację Terraform o instancję Cloud SQL z dwoma osobnymi bazami danych - jedną dla dev, jedną dla prod. Hasło do bazy powinno trafić do Secret Manager, nie do repozytorium.

Symfony łączy się z bazą przez zmienną środowiskową `DATABASE_URL`. Pipeline CI/CD przekazuje właściwą wartość do właściwego środowiska.

## Wskazówki

- Zasoby Terraform: `google_sql_database_instance`, `google_sql_database`, `google_sql_user`
- Baza: PostgreSQL 15+, najtańszy tier (`db-f1-micro`) wystarczy
- Cloud Run łączy się z Cloud SQL przez Cloud SQL Auth Proxy - potrzebna flaga `--add-cloudsql-instances` i uprawnienie `roles/cloudsql.client` dla Service Account
- Format `DATABASE_URL` przy połączeniu przez proxy: `postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE`
- Migracje Doctrine można uruchamiać jako Cloud Run Job lub jako krok w pipeline

## Automatyczne zatrzymywanie instancji

Cloud SQL kosztuje ~$7-10/miesiąc nawet gdy nie używasz. Skonfiguruj automatyczne zatrzymywanie przez Cloud Scheduler.

Dodaj do Terraform:
- zasób `google_cloud_scheduler_job` który codziennie o określonej godzinie wywołuje Cloud SQL Admin API i ustawia `activationPolicy: NEVER`
- potrzebny Service Account z uprawnieniem `roles/cloudsql.editor`
- wywołanie przez HTTP target na endpoint `https://sqladmin.googleapis.com/sql/v1beta4/projects/PROJECT/instances/INSTANCE`

Ustaw godzinę zatrzymania odpowiednio do harmonogramu zajęć (np. 20:00 w dniu zajęć, lub codziennie na wszelki wypadek).

Możesz też dodać job który włącza instancję przed zajęciami.

## Checkpoint

- [ ] Terraform tworzy instancję Cloud SQL
- [ ] Dwie osobne bazy: dev i prod
- [ ] Hasło w Secret Manager
- [ ] Aplikacja na DEV łączy się z bazą dev, PROD z bazą prod
- [ ] Migracje wykonywane automatycznie przy deploy
- [ ] Cloud Scheduler zatrzymuje instancję automatycznie po zajęciach
