package products

import cats.effect.*
import org.http4s.*
import org.http4s.circe.*
import org.http4s.dsl.io.*

object Routes:
  given EntityDecoder[IO, ProductInput] = jsonOf[IO, ProductInput]

  def apply(ctrl: ProductController, sportCtrl: SportProductController): HttpRoutes[IO] =
    HttpRoutes.of[IO]:
      case GET -> Root / "products"        => ctrl.list
      case req @ POST -> Root / "products" => req.as[ProductInput].flatMap(ctrl.create)

      case GET -> Root / "sport-products" / "search" :? QueryParam(q) +& LimitParam(limit) +& ModelParam(model) => sportCtrl.search(q, limit.getOrElse(10), model.getOrElse("ollama"))
      case GET -> Root / "sport-products" / LongVar(id)               => sportCtrl.getById(id)
      case GET -> Root / "sport-products"   :? NameParam(name)        => sportCtrl.findByName(name)
      case GET -> Root / "sport-products"                              => sportCtrl.listAll

  object NameParam  extends QueryParamDecoderMatcher[String]("name")
  object QueryParam extends QueryParamDecoderMatcher[String]("q")
  object LimitParam extends OptionalQueryParamDecoderMatcher[Int]("limit")
  object ModelParam extends OptionalQueryParamDecoderMatcher[String]("model")
