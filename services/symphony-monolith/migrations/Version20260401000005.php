<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000005 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add super_seller_id FK to offer table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE offer ADD super_seller_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE offer ADD CONSTRAINT FK_offer_super_seller FOREIGN KEY (super_seller_id) REFERENCES super_seller (id) NOT DEFERRABLE INITIALLY IMMEDIATE');
        $this->addSql('CREATE INDEX IDX_offer_super_seller_id ON offer (super_seller_id)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE offer DROP CONSTRAINT FK_offer_super_seller');
        $this->addSql('DROP INDEX IDX_offer_super_seller_id');
        $this->addSql('ALTER TABLE offer DROP super_seller_id');
    }
}
