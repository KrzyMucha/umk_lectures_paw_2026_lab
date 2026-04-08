<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000006 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add nullable super_seller_id relation to user (idempotent)';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS super_seller_id INT DEFAULT NULL');
        $this->addSql('CREATE INDEX IF NOT EXISTS IDX_user_super_seller_id ON "user" (super_seller_id)');

        $this->addSql('DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = \'fk_user_super_seller\') THEN
                ALTER TABLE "user" ADD CONSTRAINT FK_user_super_seller FOREIGN KEY (super_seller_id) REFERENCES super_seller (id) NOT DEFERRABLE INITIALLY IMMEDIATE;
            END IF;
        END $$');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE "user" DROP CONSTRAINT IF EXISTS FK_user_super_seller');
        $this->addSql('DROP INDEX IF EXISTS IDX_user_super_seller_id');
        $this->addSql('ALTER TABLE "user" DROP COLUMN IF EXISTS super_seller_id');
    }
}