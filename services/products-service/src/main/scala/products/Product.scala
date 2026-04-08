package products

import io.circe.*
import io.circe.generic.semiauto.*

case class Product(id: Int, name: String, description: Option[String], price: Double)

object Product:
  given Encoder[Product] = deriveEncoder
