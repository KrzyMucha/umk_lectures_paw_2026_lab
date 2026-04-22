package products

import cats.effect.*
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.implicits.*
import com.comcast.ip4s.*

object Main extends IOApp.Simple:

  def run: IO[Unit] =
    for
      ctrl    <- ProductController.make
      portNum  = sys.env.getOrElse("PORT", "8081").toInt
      port     = Port.fromInt(portNum).getOrElse(port"8081")
      _       <- IO.println(s"products-service starting on port $portNum ...") >>
                   EmberServerBuilder.default[IO]
                     .withHost(ipv4"0.0.0.0")
                     .withPort(port)
                     .withHttpApp(Routes(ctrl).orNotFound)
                     .build
                     .useForever
    yield ()
