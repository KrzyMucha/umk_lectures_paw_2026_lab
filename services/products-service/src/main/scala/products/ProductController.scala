package products

import cats.effect.*
import cats.effect.kernel.Ref
import io.circe.*
import io.circe.syntax.*
import org.http4s.*
import org.http4s.circe.jsonEncoder
import org.http4s.dsl.io.*

object ProductController:
  private val initialProducts: Map[Int, Product] = Map(
    1 -> Product(1, "Laptop Pro", Some("High-end laptop for developers"), 2999.99),
    2 -> Product(2, "Mechanical Keyboard", Some("RGB mechanical keyboard TKL"), 349.00),
    3 -> Product(3, "USB-C Hub", None, 89.99),
  )

  def make: IO[ProductController] =
    Ref.of[IO, Map[Int, Product]](initialProducts).map(new ProductController(_))

class ProductController(store: Ref[IO, Map[Int, Product]]):

  def list: IO[Response[IO]] =
    store.get.flatMap(m => Ok(m.values.toList.sortBy(_.id).asJson))

  def create(input: ProductInput): IO[Response[IO]] =
    input.name.map(_.trim).filter(_.nonEmpty) match
      case None =>
        BadRequest(Json.obj("error" -> Json.fromString("Name is required")))
      case Some(name) =>
        input.price match
          case None =>
            BadRequest(Json.obj("error" -> Json.fromString("Price must be numeric")))
          case Some(price) =>
            store.modify: m =>
              val id      = m.keys.maxOption.getOrElse(0) + 1
              val product = Product(id, name, input.description, price)
              (m + (id -> product), product)
            .flatMap(product => Created(product.asJson))
