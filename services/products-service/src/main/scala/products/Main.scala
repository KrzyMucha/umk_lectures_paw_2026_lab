package products

import cats.effect.*
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.implicits.*
import com.comcast.ip4s.*

object Main extends IOApp.Simple:

  def run: IO[Unit] =
    val dbUrl = sys.env.getOrElse("DATABASE_URL", throw RuntimeException("DATABASE_URL is required"))
    val portNum = sys.env.getOrElse("PORT", "8081").toInt
    val port    = Port.fromInt(portNum).getOrElse(port"8081")

    Database.transactor(dbUrl).use: xa =>
      val repo = ProductRepository(xa)
      val ctrl = ProductController(repo)
      IO.println(s"products-service starting on port $portNum ...") >>
        EmberServerBuilder.default[IO]
          .withHost(ipv4"0.0.0.0")
          .withPort(port)
          .withHttpApp(Routes(ctrl).orNotFound)
          .build
          .useForever

