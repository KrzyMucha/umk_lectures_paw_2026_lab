<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260330000002 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Drop product_review table and sequence; keep product-only schema';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('DROP TABLE IF EXISTS product_review CASCADE');
        $this->addSql('DROP SEQUENCE IF EXISTS product_review_id_seq CASCADE');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE product_review_id_seq INCREMENT BY 1 MINVALUE 1 START 1');

        $this->addSql('CREATE TABLE product_review (
            id INT NOT NULL,
            product_id INT NOT NULL,
            rating SMALLINT NOT NULL,
            comment TEXT DEFAULT NULL,
            author_name VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            PRIMARY KEY(id)
        )');

        $this->addSql('ALTER TABLE product_review ADD CONSTRAINT FK_product_review_product FOREIGN KEY (product_id) REFERENCES product (id) NOT DEFERRABLE INITIALLY IMMEDIATE');
        $this->addSql('CREATE INDEX IDX_product_review_product_id ON product_review (product_id)');
        $this->addSql("COMMENT ON COLUMN product_review.created_at IS '(DC2Type:datetime_immutable)'");
    }
}
