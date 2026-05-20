package products

import io.circe.*
import io.circe.generic.semiauto.*

case class SportProduct(
  id:          Long,
  name:        String,
  description: Option[String],
  price:       Double,
  player:      String,
  game_date:   String,
  opponent:    String,
  points:      Int,
  rebounds:    Int,
  assists:     Int,
  steals:      Int,
  blocks:      Int,
)

object SportProduct:
  given Decoder[SportProduct] = (c: HCursor) =>
    for
      name        <- c.downField("name").as[String]
      description <- c.downField("description").as[Option[String]]
      price       <- c.downField("price").as[Double]
      player      <- c.downField("player").as[String]
      game_date   <- c.downField("game_date").as[String]
      opponent    <- c.downField("opponent").as[String]
      points      <- c.downField("points").as[Int]
      rebounds    <- c.downField("rebounds").as[Int]
      assists     <- c.downField("assists").as[Int]
      steals      <- c.downField("steals").as[Int]
      blocks      <- c.downField("blocks").as[Int]
    yield SportProduct(0L, name, description, price, player, game_date, opponent, points, rebounds, assists, steals, blocks)

  given Encoder[SportProduct] = deriveEncoder
