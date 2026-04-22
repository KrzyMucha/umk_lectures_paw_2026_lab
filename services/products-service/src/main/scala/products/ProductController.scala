package products

import cats.effect.*
import io.circe.*
import io.circe.syntax.*
import org.http4s.*
import org.http4s.circe.jsonEncoder
import org.http4s.dsl.io.*

class ProductController(repo: ProductRepository):

  def list: IO[Response[IO]] =
    repo.findAll.flatMap(products => Ok(products.asJson))

  def create(input: ProductInput): IO[Response[IO]] =
    input.name.map(_.trim).filter(_.nonEmpty) match
      case None =>
        BadRequest(Json.obj("error" -> Json.fromString("Name is required")))
      case Some(name) =>
        input.price match
          case None =>
            BadRequest(Json.obj("error" -> Json.fromString("Price must be numeric")))
          case Some(price) =>
            repo.insert(name, input.description, price).flatMap(p => Created(p.asJson))
