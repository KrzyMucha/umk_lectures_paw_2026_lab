package products

import cats.effect.*
import cats.effect.kernel.Ref
import io.circe.*
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import org.http4s.*
import org.http4s.circe.*
import org.http4s.dsl.io.*
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.implicits.*
import com.comcast.ip4s.*

case class Product(id: Int, name: String, description: Option[String], price: Double)

object Product:
  given Encoder[Product] = deriveEncoder

case class ProductInput(name: Option[String], description: Option[String], price: Option[Double])

object ProductInput:
  given Decoder[ProductInput] = deriveDecoder

object Main extends IOApp.Simple:

  val initialProducts: Map[Int, Product] = Map(
    1 -> Product(1, "Laptop Pro", Some("High-end laptop for developers"), 2999.99),
    2 -> Product(2, "Mechanical Keyboard", Some("RGB mechanical keyboard TKL"), 349.00),
    3 -> Product(3, "USB-C Hub", None, 89.99),
  )

  given EntityDecoder[IO, ProductInput] = jsonOf[IO, ProductInput]

  def routes(store: Ref[IO, Map[Int, Product]], counter: Ref[IO, Int]): HttpRoutes[IO] =
    HttpRoutes.of[IO]:

      case GET -> Root / "products" =>
        store.get.flatMap: m =>
          Ok(m.values.toList.sortBy(_.id).asJson)

      case req @ POST -> Root / "products" =>
        req.as[ProductInput].flatMap: input =>
          input.name.map(_.trim).filter(_.nonEmpty) match
            case None =>
              BadRequest(Json.obj("error" -> Json.fromString("Name is required")))
            case Some(name) =>
              input.price match
                case None =>
                  BadRequest(Json.obj("error" -> Json.fromString("Price must be numeric")))
                case Some(price) =>
                  counter.updateAndGet(_ + 1).flatMap: id =>
                    val product = Product(id, name, input.description, price)
                    store.update(_ + (id -> product)) >>
                      Created(product.asJson)

  def run: IO[Unit] =
    for
      store   <- Ref.of[IO, Map[Int, Product]](initialProducts)
      counter <- Ref.of[IO, Int](initialProducts.size)
      portNum  = sys.env.getOrElse("PORT", "8081").toInt
      port     = Port.fromInt(portNum).getOrElse(port"8081")
      _       <- IO.println(s"products-service starting on port $portNum ...") >>
                   EmberServerBuilder
                     .default[IO]
                     .withHost(ipv4"0.0.0.0")
                     .withPort(port)
                     .withHttpApp(routes(store, counter).orNotFound)
                     .build
                     .useForever
    yield ()
