<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000001 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create offer table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE offer_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('CREATE TABLE offer (
            id INT NOT NULL DEFAULT nextval(\'offer_id_seq\'),
            title VARCHAR(255) NOT NULL,
            description TEXT DEFAULT NULL,
            price DOUBLE PRECISION NOT NULL,
            PRIMARY KEY(id)
        )');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE offer');
        $this->addSql('DROP SEQUENCE offer_id_seq');
    }
}
