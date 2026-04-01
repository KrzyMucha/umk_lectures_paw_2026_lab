<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000003 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create purchase table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE purchase_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('CREATE TABLE purchase (
            id INT NOT NULL DEFAULT nextval(\'purchase_id_seq\'),
            user_id INT NOT NULL,
            offer_id INT NOT NULL,
            quantity INT NOT NULL,
            price_per_unit DOUBLE PRECISION NOT NULL,
            status VARCHAR(32) NOT NULL,
            PRIMARY KEY(id)
        )');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE purchase');
        $this->addSql('DROP SEQUENCE purchase_id_seq');
    }
}
