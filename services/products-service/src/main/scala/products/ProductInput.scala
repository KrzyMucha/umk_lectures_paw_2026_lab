package products

import io.circe.*
import io.circe.generic.semiauto.*

case class ProductInput(name: Option[String], description: Option[String], price: Option[Double])

object ProductInput:
  given Decoder[ProductInput] = deriveDecoder
