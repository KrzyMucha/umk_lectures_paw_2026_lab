package products

import cats.effect.*
import doobie.*
import doobie.implicits.*
import doobie.postgres.circe.json.implicits.*
import io.circe.Json

class SportProductRepository(xa: Transactor[IO]):

  private def toSportProduct(id: Long, data: Json): Option[SportProduct] =
    data.as[SportProduct].toOption.map(_.copy(id = id))

  def findAll: IO[List[SportProduct]] =
    sql"SELECT id, data FROM product ORDER BY id"
      .query[(Long, Json)].to[List].transact(xa)
      .map(_.flatMap(toSportProduct))

  def findById(id: Long): IO[Option[SportProduct]] =
    sql"SELECT id, data FROM product WHERE id = $id"
      .query[(Long, Json)].option.transact(xa)
      .map(_.flatMap(toSportProduct))

  def findByNameSubstring(name: String): IO[List[SportProduct]] =
    findAll.map(_.filter(_.name.toLowerCase.contains(name.toLowerCase)))

  def findSimilar(embedding: Vector[Float], limit: Int): IO[List[SportProduct]] =
    val vec = embedding.mkString("[", ",", "]")
    (fr"SELECT id, data FROM product WHERE embedding IS NOT NULL ORDER BY embedding <=>" ++
      Fragment.const(s"'$vec'::vector") ++
      fr"LIMIT $limit")
      .query[(Long, Json)].to[List].transact(xa)
      .map(_.flatMap(toSportProduct))

  def findSimilarGemini(embedding: Vector[Float], limit: Int): IO[List[SportProduct]] =
    val vec = embedding.mkString("[", ",", "]")
    (fr"SELECT id, data FROM product WHERE embedding_gemini IS NOT NULL ORDER BY embedding_gemini <=>" ++
      Fragment.const(s"'$vec'::vector") ++
      fr"LIMIT $limit")
      .query[(Long, Json)].to[List].transact(xa)
      .map(_.flatMap(toSportProduct))

