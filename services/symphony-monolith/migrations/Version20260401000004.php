<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260401000004 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Recreate product_review table with FK to product and add super_seller relation to user';
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE SEQUENCE product_review_id_seq INCREMENT BY 1 MINVALUE 1 START 1');

        $this->addSql('CREATE TABLE product_review (
            id INT NOT NULL DEFAULT nextval(\'product_review_id_seq\'),
            product_id INT NOT NULL,
            rating SMALLINT NOT NULL,
            comment TEXT DEFAULT NULL,
            author_name VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            PRIMARY KEY(id)
        )');

        $this->addSql('ALTER SEQUENCE product_review_id_seq OWNED BY product_review.id');
        $this->addSql('ALTER TABLE product_review ADD CONSTRAINT FK_product_review_product FOREIGN KEY (product_id) REFERENCES product (id) NOT DEFERRABLE INITIALLY IMMEDIATE');
        $this->addSql('CREATE INDEX IDX_product_review_product_id ON product_review (product_id)');
        $this->addSql("COMMENT ON COLUMN product_review.created_at IS '(DC2Type:datetime_immutable)'");

        $this->addSql('CREATE SEQUENCE super_seller_id_seq INCREMENT BY 1 MINVALUE 1 START 1');
        $this->addSql('CREATE TABLE super_seller (
            id INT NOT NULL DEFAULT nextval(\'super_seller_id_seq\'),
            name VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL,
            created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
            PRIMARY KEY(id)
        )');
        $this->addSql('ALTER SEQUENCE super_seller_id_seq OWNED BY super_seller.id');
        $this->addSql("COMMENT ON COLUMN super_seller.created_at IS '(DC2Type:datetime_immutable)'");

        $this->addSql('ALTER TABLE "user" ADD super_seller_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE "user" ADD CONSTRAINT FK_user_super_seller FOREIGN KEY (super_seller_id) REFERENCES super_seller (id) NOT DEFERRABLE INITIALLY IMMEDIATE');
        $this->addSql('CREATE INDEX IDX_user_super_seller_id ON "user" (super_seller_id)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE "user" DROP CONSTRAINT IF EXISTS FK_user_super_seller');
        $this->addSql('DROP INDEX IF EXISTS IDX_user_super_seller_id');
        $this->addSql('ALTER TABLE "user" DROP COLUMN IF EXISTS super_seller_id');

        $this->addSql('DROP TABLE IF EXISTS super_seller CASCADE');
        $this->addSql('DROP SEQUENCE IF EXISTS super_seller_id_seq CASCADE');

        $this->addSql('DROP TABLE IF EXISTS product_review CASCADE');
        $this->addSql('DROP SEQUENCE IF EXISTS product_review_id_seq CASCADE');
    }
}
