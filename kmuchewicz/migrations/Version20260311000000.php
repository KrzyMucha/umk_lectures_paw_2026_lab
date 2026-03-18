<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260311000000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create offers table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE TABLE offers (
            id          SERIAL          NOT NULL,
            title       VARCHAR(255)    NOT NULL,
            description TEXT            DEFAULT NULL,
            price       NUMERIC(10, 2)  NOT NULL,
            created_at  TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            updated_at  TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            PRIMARY KEY(id)
        )');

        $this->addSql("COMMENT ON COLUMN offers.created_at IS '(DC2Type:datetime_immutable)'");
        $this->addSql("COMMENT ON COLUMN offers.updated_at IS '(DC2Type:datetime_immutable)'");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE offers');
    }
}
