package products

import cats.effect.*
import doobie.*
import doobie.implicits.*

class ProductRepository(xa: Transactor[IO]):

  def findAll: IO[List[Product]] =
    sql"SELECT id, name, description, price FROM product ORDER BY id"
      .query[Product]
      .to[List]
      .transact(xa)

  def insert(name: String, description: Option[String], price: Double): IO[Product] =
    sql"""
      INSERT INTO product (id, name, description, price)
      VALUES (nextval('product_id_seq'), $name, $description, $price)
      RETURNING id, name, description, price
    """.query[Product].unique.transact(xa)
