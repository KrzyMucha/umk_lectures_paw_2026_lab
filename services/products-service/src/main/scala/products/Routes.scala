package products

import cats.effect.*
import org.http4s.*
import org.http4s.circe.*
import org.http4s.dsl.io.*

object Routes:
  given EntityDecoder[IO, ProductInput] = jsonOf[IO, ProductInput]

  def apply(ctrl: ProductController): HttpRoutes[IO] =
    HttpRoutes.of[IO]:
      case GET -> Root / "products"        => ctrl.list
      case req @ POST -> Root / "products" => req.as[ProductInput].flatMap(ctrl.create)
