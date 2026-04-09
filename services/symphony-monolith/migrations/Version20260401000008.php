<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000008 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add offer_id FK to product_review table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE product_review ADD offer_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE product_review ADD CONSTRAINT FK_product_review_offer FOREIGN KEY (offer_id) REFERENCES offer (id) NOT DEFERRABLE INITIALLY IMMEDIATE');
        $this->addSql('CREATE INDEX IDX_product_review_offer_id ON product_review (offer_id)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE product_review DROP CONSTRAINT FK_product_review_offer');
        $this->addSql('DROP INDEX IDX_product_review_offer_id');
        $this->addSql('ALTER TABLE product_review DROP COLUMN offer_id');
    }
}
