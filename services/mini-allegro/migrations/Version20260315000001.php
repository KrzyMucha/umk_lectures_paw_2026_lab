<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260315000001 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create product and product_review tables';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE product_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('CREATE SEQUENCE product_review_id_seq INCREMENT BY 1 MINVALUE 1 START 1');

        $this->addSql('
            CREATE TABLE product (
                id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT DEFAULT NULL,
                price NUMERIC(10, 2) NOT NULL,
                PRIMARY KEY(id)
            )
        ');

        $this->addSql('
            CREATE TABLE product_review (
                id INT NOT NULL,
                product_id INT NOT NULL,
                rating SMALLINT NOT NULL,
                comment TEXT DEFAULT NULL,
                author_name VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
                PRIMARY KEY(id)
            )
        ');

        $this->addSql('
            ALTER TABLE product_review
            ADD CONSTRAINT FK_product_review_product
            FOREIGN KEY (product_id) REFERENCES product (id) NOT DEFERRABLE INITIALLY IMMEDIATE
        ');

        $this->addSql('CREATE INDEX IDX_product_review_product_id ON product_review (product_id)');

        $this->addSql("COMMENT ON COLUMN product_review.created_at IS '(DC2Type:datetime_immutable)'");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE product_review DROP CONSTRAINT FK_product_review_product');
        $this->addSql('DROP TABLE product_review');
        $this->addSql('DROP TABLE product');
        $this->addSql('DROP SEQUENCE product_id_seq CASCADE');
        $this->addSql('DROP SEQUENCE product_review_id_seq CASCADE');
    }
}
