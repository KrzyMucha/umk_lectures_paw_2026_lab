<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000007 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add nullable super_seller_id FK to purchase table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE purchase ADD super_seller_id INT DEFAULT NULL');
        $this->addSql('CREATE INDEX IDX_purchase_super_seller_id ON purchase (super_seller_id)');
        $this->addSql("DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='super_sellers') THEN ALTER TABLE purchase ADD CONSTRAINT FK_purchase_super_seller FOREIGN KEY (super_seller_id) REFERENCES super_sellers (id) NOT DEFERRABLE INITIALLY IMMEDIATE; END IF; END $$;");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE purchase DROP CONSTRAINT IF EXISTS FK_purchase_super_seller');
        $this->addSql('DROP INDEX IF EXISTS IDX_purchase_super_seller_id');
        $this->addSql('ALTER TABLE purchase DROP COLUMN super_seller_id');
    }
}
