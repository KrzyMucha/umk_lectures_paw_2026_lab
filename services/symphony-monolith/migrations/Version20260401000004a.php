<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000004a extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create super_seller table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE IF NOT EXISTS super_seller_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('CREATE TABLE IF NOT EXISTS super_seller (
            id INT NOT NULL DEFAULT nextval(\'super_seller_id_seq\'),
            name VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            PRIMARY KEY(id)
        )');
        $this->addSql('ALTER SEQUENCE super_seller_id_seq OWNED BY super_seller.id');
        $this->addSql("COMMENT ON COLUMN super_seller.created_at IS '(DC2Type:datetime_immutable)'");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE IF EXISTS super_seller CASCADE');
        $this->addSql('DROP SEQUENCE IF EXISTS super_seller_id_seq CASCADE');
    }
}
