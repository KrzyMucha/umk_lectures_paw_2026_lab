<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260330000003 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Fix product.id sequence default for PostgreSQL inserts';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE IF NOT EXISTS product_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('ALTER SEQUENCE product_id_seq OWNED BY product.id');
        $this->addSql("ALTER TABLE product ALTER COLUMN id SET DEFAULT nextval('product_id_seq')");
        $this->addSql("SELECT setval('product_id_seq', COALESCE((SELECT MAX(id) + 1 FROM product), 1), false)");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE product ALTER COLUMN id DROP DEFAULT');
    }
}
