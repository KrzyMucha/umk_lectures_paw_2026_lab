<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000002 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create user table for App\\Entity\\User';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE user_id_seq INCREMENT BY 1 MINVALUE 1 START 1');

        $this->addSql('
            CREATE TABLE "user" (
                id INT NOT NULL,
                email VARCHAR(255) NOT NULL,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                roles TEXT NOT NULL,
                PRIMARY KEY(id)
            )
        ');

        $this->addSql('ALTER SEQUENCE user_id_seq OWNED BY "user".id');
        $this->addSql("ALTER TABLE \"user\" ALTER COLUMN id SET DEFAULT nextval('user_id_seq')");
        $this->addSql('CREATE UNIQUE INDEX UNIQ_user_email ON "user" (email)');
        $this->addSql("SELECT setval('user_id_seq', COALESCE((SELECT MAX(id) + 1 FROM \"user\"), 1), false)");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE "user"');
        $this->addSql('DROP SEQUENCE user_id_seq CASCADE');
    }
}
